import pytest
import os
import multiprocessing
import json
from utils.device_manager import DeviceManager
from utils.yaml_utils import load_yaml
from utils.screenshot_util import screenshot_util
from utils.logger import log
from datetime import datetime
import re

# 全局队列用于收集测试结果
test_results_queue = multiprocessing.Queue()

def get_device_ids():
    """
    Get list of device IDs from the configuration
    
    Returns:
        list: List of device IDs
    """
    devices_path = os.path.join(os.path.dirname(__file__), 'config', 'devices.yaml')
    devices_data = load_yaml(devices_path)
    return [device.get('id') for device in devices_data.get('devices', [])]

def pytest_addoption(parser):
    """
    Add command line options for test configuration
    """
    parser.addoption("--device-id", action="store", default=None,
                     help="Specify a device ID from the config to run tests on")
    # pytest-rerunfailures 插件已经添加了 --reruns 和 --reruns-delay 选项，不需要重复添加

def pytest_generate_tests(metafunc):
    """
    Generate test parameters
    """
    # If a test requires a device_id parameter, parametrize it with available device IDs
    if "device_id" in metafunc.fixturenames:
        # If specific device ID is provided via command line, use only that one
        specific_device_id = metafunc.config.getoption("--device-id")
        if specific_device_id:
            metafunc.parametrize("device_id", [specific_device_id])
        else:
            # Otherwise, use all available device IDs
            metafunc.parametrize("device_id", get_device_ids())

@pytest.fixture(scope="function")
def device_id(request):
    """
    Fixture to provide device ID
    """
    return request.param

@pytest.fixture(scope="function")
def device(device_id, request):
    """
    Fixture to provide a connected device
    
    Args:
        device_id: The device ID to connect to
        
    Yields:
        uiautomator2.Device: Connected device object
    """
    log.info(f"设置 device_id={device_id} 的测试环境")
    
    # Initialize and connect device
    device_manager = DeviceManager(device_id)
    device = device_manager.connect()
    
    # Start the application
    device_manager.start_app()
    
    # Yield the device for the test
    yield device
    
    # Clean up after test
    log.info(f"清理 device_id={device_id} 的测试环境")
    device_manager.disconnect()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # 执行测试
    outcome = yield
    report = outcome.get_result()
    
    # 测试失败时截图
    if report.when == "call" and report.failed:
        try:
            # 获取device fixture
            device = item.funcargs.get("device")
            if device:
                log.error(f"测试失败: {item.nodeid}")
                screenshot_path = screenshot_util.take_screenshot(
                    device, 
                    item.nodeid
                )
                
                # 如果使用了pytest-html，将截图添加到报告
                if hasattr(item.config, "_html"):
                    # 将截图作为额外附件添加到报告
                    if screenshot_path and os.path.exists(screenshot_path):
                        html = '<div><img src="{}" alt="screenshot" style="width:600px;height:auto;" /></div>'.format(
                            screenshot_path
                        )
                        # 在附加HTML中添加图片
                        extra = getattr(report, "extra", [])
                        extra.append(pytest.html.extras.html(html))
                        setattr(report, "extra", extra)
        except Exception as e:
            log.error(f"测试失败后截图出错: {str(e)}")

def run_test_on_device(device_id, test_module, results_queue):
    """
    Run tests on a specific device
    
    Args:
        device_id (str): Device ID to run tests on
        test_module (str): Test module to run
        results_queue: 多进程队列，用于收集测试结果
    """
    log.info(f"开始在设备 {device_id} 上运行测试")
    
    # 为每个设备生成一个临时的JSON结果文件
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    json_result_file = os.path.join(temp_dir, f"results_{device_id}.json")
    
    # 执行测试，使用--json-report参数而不是--json
    exit_code = pytest.main([
        test_module,
        f"--device-id={device_id}",
        "-v",
        "--json-report",
        f"--json-report-file={json_result_file}",
        "--reruns=2",        # 失败重试2次
        "--reruns-delay=1"   # 重试间隔1秒
    ])
    
    # 将设备ID和结果文件路径放入队列
    results_queue.put({
        'device_id': device_id,
        'result_file': json_result_file,
        'exit_code': exit_code
    })
    
    log.info(f"设备 {device_id} 的测试完成，退出代码: {exit_code}")

def run_tests_in_parallel(test_module):
    """
    Run tests in parallel on all available devices
    
    Args:
        test_module (str): Test module to run
    """
    device_ids = get_device_ids()
    processes = []
    
    log.info(f"开始在 {len(device_ids)} 台设备上并行运行测试: {device_ids}")
    
    # 使用多进程队列收集结果
    results_queue = multiprocessing.Queue()
    
    # 创建临时目录
    temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    for device_id in device_ids:
        process = multiprocessing.Process(
            target=run_test_on_device,
            args=(device_id, test_module, results_queue)
        )
        processes.append(process)
        process.start()
    
    # 等待所有进程完成
    for process in processes:
        process.join()
    
    log.info("所有设备测试进程已完成，正在生成统一测试报告...")
    
    # 从队列中收集所有设备的测试结果
    all_results = []
    while not results_queue.empty():
        result = results_queue.get()
        all_results.append(result)
    
    # 生成统一的HTML报告
    generate_combined_report(all_results, test_module)

def generate_combined_report(test_results, test_module):
    """
    生成包含所有设备测试结果的统一HTML报告
    
    Args:
        test_results (list): 包含每个设备测试结果的列表
        test_module (str): 测试模块名称
    """
    # 创建报告目录
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # 生成报告文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(reports_dir, f"combined_report_{timestamp}.html")
    
    # 创建HTML报告内容
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>多设备测试报告</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                line-height: 1.6;
            }}
            h1 {{
                color: #333;
                border-bottom: 2px solid #eee;
                padding-bottom: 10px;
            }}
            .device-section {{
                margin-bottom: 30px;
                border: 1px solid #ddd;
                padding: 15px;
                border-radius: 5px;
            }}
            .device-header {{
                background-color: #f5f5f5;
                padding: 10px;
                margin: -15px -15px 15px -15px;
                border-bottom: 1px solid #ddd;
                border-radius: 5px 5px 0 0;
            }}
            .pass {{
                color: green;
            }}
            .fail {{
                color: red;
            }}
            .summary {{
                margin-bottom: 20px;
                font-size: 1.1em;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
        </style>
    </head>
    <body>
        <h1>Android UI 自动化测试报告</h1>
        <div class="summary">
            <p>测试模块: <strong>{test_module}</strong></p>
            <p>执行时间: <strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</strong></p>
            <p>测试设备数量: <strong>{len(test_results)}</strong></p>
        </div>
    """
    
    # 添加每个设备的测试结果
    for result in test_results:
        device_id = result['device_id']
        result_file = result['result_file']
        exit_code = result['exit_code']
        
        # 读取JSON结果文件
        if os.path.exists(result_file):
            try:
                with open(result_file, 'r') as f:
                    json_data = json.load(f)
                
                # 获取测试统计信息
                summary = json_data.get('summary', {})
                total = summary.get('total', 0)
                passed = summary.get('passed', 0)
                failed = summary.get('failed', 0)
                skipped = summary.get('skipped', 0)
                
                # 添加设备测试结果到HTML
                status_class = "pass" if exit_code == 0 else "fail"
                
                html_content += f"""
                <div class="device-section">
                    <div class="device-header">
                        <h2>设备: {device_id}</h2>
                        <p class="{status_class}">状态: {'通过' if exit_code == 0 else '失败'}</p>
                    </div>
                    <div class="device-summary">
                        <p>总用例数: {total}</p>
                        <p>通过: <span class="pass">{passed}</span></p>
                        <p>失败: <span class="fail">{failed}</span></p>
                        <p>跳过: {skipped}</p>
                    </div>
                """
                
                # 添加测试用例详情
                tests = json_data.get('tests', [])
                if tests:
                    html_content += """
                    <table>
                        <tr>
                            <th>测试用例</th>
                            <th>结果</th>
                            <th>耗时 (秒)</th>
                        </tr>
                    """
                    
                    for test in tests:
                        name = test.get('name', '')
                        nodeid = test.get('nodeid', '')
                        # Extract just the test name from the nodeid for better readability
                        if not name and nodeid:
                            # Extract the test method name from the nodeid
                            # From format like "tests/test_login.py::TestLogin::test_successful_login[device1]"
                            # to just "test_successful_login"
                            match = re.search(r'::([^:]+)(\[|$)', nodeid)
                            if match:
                                name = match.group(1)
                            else:
                                name = nodeid.split('::')[-1] if '::' in nodeid else nodeid
                                
                        outcome = test.get('outcome', '')
                        
                        # Get duration from the "call" section instead of top-level
                        call_data = test.get('call', {})
                        duration = call_data.get('duration', 0)
                        
                        outcome_class = "pass" if outcome == "passed" else "fail" if outcome == "failed" else ""
                        outcome_text = "通过" if outcome == "passed" else "失败" if outcome == "failed" else "跳过"
                        
                        html_content += f"""
                        <tr>
                            <td>{name}</td>
                            <td class="{outcome_class}">{outcome_text}</td>
                            <td>{duration:.2f}</td>
                        </tr>
                        """
                    
                    html_content += "</table>"
                
                html_content += "</div>"  # 结束设备部分
                
            except Exception as e:
                log.error(f"读取结果文件失败: {result_file}, 错误: {str(e)}")
                html_content += f"""
                <div class="device-section">
                    <div class="device-header">
                        <h2>设备: {device_id}</h2>
                        <p class="fail">状态: 错误</p>
                    </div>
                    <p>无法读取测试结果: {str(e)}</p>
                </div>
                """
        else:
            log.error(f"结果文件不存在: {result_file}")
            html_content += f"""
            <div class="device-section">
                <div class="device-header">
                    <h2>设备: {device_id}</h2>
                    <p class="fail">状态: 错误</p>
                </div>
                <p>未找到测试结果文件</p>
            </div>
            """
    
    # 完成HTML
    html_content += """
    </body>
    </html>
    """
    
    # 写入HTML文件
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    log.info(f"统一测试报告已生成: {report_file}")

if __name__ == "__main__":
    # This allows running tests in parallel directly by executing this file
    import sys
    
    if len(sys.argv) > 1:
        test_module = sys.argv[1]
    else:
        test_module = "tests/test_login.py"
    
    run_tests_in_parallel(test_module) 