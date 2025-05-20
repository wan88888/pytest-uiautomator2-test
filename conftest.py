import pytest
import os
import multiprocessing
from utils.device_manager import DeviceManager
from utils.yaml_utils import load_yaml
from datetime import datetime

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
def device(device_id):
    """
    Fixture to provide a connected device
    
    Args:
        device_id: The device ID to connect to
        
    Yields:
        uiautomator2.Device: Connected device object
    """
    # Initialize and connect device
    device_manager = DeviceManager(device_id)
    device = device_manager.connect()
    
    # Start the application
    device_manager.start_app()
    
    # Yield the device for the test
    yield device
    
    # Clean up after test
    device_manager.disconnect()

def run_test_on_device(device_id, test_module):
    """
    Run tests on a specific device
    
    Args:
        device_id (str): Device ID to run tests on
        test_module (str): Test module to run
    """
    print(f"Running tests on device {device_id}")
    
    # 创建报告目录
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # 生成带时间戳的报告文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(reports_dir, f"report_{device_id}_{timestamp}.html")
    
    pytest.main([
        test_module,
        f"--device-id={device_id}",
        "-v",
        f"--html={report_file}",
        "--self-contained-html"
    ])
    
    print(f"Test report for device {device_id} generated at: {report_file}")

def run_tests_in_parallel(test_module):
    """
    Run tests in parallel on all available devices
    
    Args:
        test_module (str): Test module to run
    """
    device_ids = get_device_ids()
    processes = []
    
    for device_id in device_ids:
        process = multiprocessing.Process(
            target=run_test_on_device,
            args=(device_id, test_module)
        )
        processes.append(process)
        process.start()
    
    # Wait for all processes to complete
    for process in processes:
        process.join()
    
    print("All test processes completed")

if __name__ == "__main__":
    # This allows running tests in parallel directly by executing this file
    import sys
    
    if len(sys.argv) > 1:
        test_module = sys.argv[1]
    else:
        test_module = "tests/test_login.py"
    
    run_tests_in_parallel(test_module) 