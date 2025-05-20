import os
import logging
import datetime

class Logger:
    """
    日志工具类，用于记录测试执行过程中的日志信息
    """
    def __init__(self, log_level=logging.INFO):
        """
        初始化日志工具
        
        Args:
            log_level: 日志级别，默认为INFO
        """
        self.logger = logging.getLogger('AndroidTestFramework')
        self.logger.setLevel(log_level)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建日志目录
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            # 生成日志文件名
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(log_dir, f'test_run_{timestamp}.log')
            
            # 添加文件处理器
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            
            # 添加控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            
            # 设置日志格式
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加处理器到logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def get_logger(self):
        """
        获取logger实例
        
        Returns:
            logging.Logger: logger实例
        """
        return self.logger
    
    def info(self, message):
        """
        记录INFO级别日志
        
        Args:
            message: 日志信息
        """
        self.logger.info(message)
    
    def debug(self, message):
        """
        记录DEBUG级别日志
        
        Args:
            message: 日志信息
        """
        self.logger.debug(message)
    
    def warning(self, message):
        """
        记录WARNING级别日志
        
        Args:
            message: 日志信息
        """
        self.logger.warning(message)
    
    def error(self, message):
        """
        记录ERROR级别日志
        
        Args:
            message: 日志信息
        """
        self.logger.error(message)
    
    def critical(self, message):
        """
        记录CRITICAL级别日志
        
        Args:
            message: 日志信息
        """
        self.logger.critical(message)

# 创建一个全局logger实例，方便直接使用
log = Logger().get_logger() 