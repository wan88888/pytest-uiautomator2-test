import os
import time
import datetime
from utils.logger import log

class ScreenshotUtil:
    """
    截图工具类，用于捕获设备屏幕截图
    """
    def __init__(self):
        """
        初始化截图工具，创建截图目录
        """
        # 创建截图目录
        self.screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'screenshots')
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def take_screenshot(self, device, test_name=None):
        """
        捕获设备当前屏幕截图
        
        Args:
            device: uiautomator2 设备对象
            test_name: 测试名称，用于生成截图文件名
            
        Returns:
            str: 截图文件的绝对路径
        """
        try:
            # 生成截图文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            device_id = device.serial
            
            if test_name:
                # 替换特殊字符，避免文件名无效
                test_name = test_name.replace('::', '_').replace('[', '_').replace(']', '_')
                screenshot_name = f"{test_name}_{device_id}_{timestamp}.png"
            else:
                screenshot_name = f"screenshot_{device_id}_{timestamp}.png"
            
            screenshot_path = os.path.join(self.screenshot_dir, screenshot_name)
            
            # 捕获截图
            device.screenshot(screenshot_path)
            log.info(f"截图已保存: {screenshot_path}")
            
            return screenshot_path
        except Exception as e:
            log.error(f"截图失败: {str(e)}")
            return None

# 创建一个全局截图工具实例，方便直接使用
screenshot_util = ScreenshotUtil() 