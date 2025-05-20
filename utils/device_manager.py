import uiautomator2 as u2
import time
from utils.yaml_utils import get_device_config

class DeviceManager:
    """
    Manager class for Android device connections
    """
    def __init__(self, device_id):
        """
        Initialize device manager for a specific device
        
        Args:
            device_id (str): Device ID from the config file
        """
        self.device_config = get_device_config(device_id)
        self.serial = self.device_config.get('serial')
        self.device = None
        
    def connect(self):
        """
        Connect to the Android device
        
        Returns:
            uiautomator2.Device: Connected device object
        """
        try:
            self.device = u2.connect(self.serial)
            # 简单检查设备是否连接成功
            self.device.info
            print(f"Connected to device {self.serial}")
            return self.device
        except Exception as e:
            raise ConnectionError(f"Failed to connect to device {self.serial}: {str(e)}")
    
    def start_app(self):
        """
        Start the target application
        """
        if not self.device:
            raise ConnectionError("Device not connected. Call connect() first.")
        
        app_package = self.device_config.get('app_package')
        app_activity = self.device_config.get('app_activity')
        
        # Stop app if it's already running
        # 使用shell命令检查应用是否在运行
        try:
            cmd = f"ps | grep {app_package}"
            output = self.device.shell(cmd)
            if app_package in output:
                # 如果应用正在运行，则先停止
                self.device.shell(f"am force-stop {app_package}")
                time.sleep(1)
        except Exception as e:
            print(f"Warning: Failed to check app status: {e}")
        
        # Start the app
        try:
            # 使用shell命令启动应用
            start_cmd = f"am start -n {app_package}/{app_activity}"
            self.device.shell(start_cmd)
            print(f"Started app {app_package} on device {self.serial}")
            time.sleep(3)  # Wait for app to initialize
        except Exception as e:
            raise RuntimeError(f"Failed to start app {app_package}: {str(e)}")
    
    def stop_app(self):
        """
        Stop the target application
        """
        if not self.device:
            return
        
        app_package = self.device_config.get('app_package')
        try:
            # 使用shell命令停止应用
            self.device.shell(f"am force-stop {app_package}")
            print(f"Stopped app {app_package} on device {self.serial}")
        except Exception as e:
            print(f"Warning: Failed to stop app {app_package}: {e}")
    
    def disconnect(self):
        """
        Disconnect from the device
        """
        if self.device:
            # Only need to stop app as u2 doesn't require explicit disconnect
            self.stop_app()
            self.device = None 