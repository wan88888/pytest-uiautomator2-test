import time
from utils.logger import log
from utils.screenshot_util import screenshot_util
from functools import wraps

def retry(max_attempts=3, delay=1):
    """
    重试装饰器，对不稳定的操作进行重试
    
    Args:
        max_attempts: 最大重试次数
        delay: 重试间隔时间(秒)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, self=None, **kwargs):
            last_exception = None
            # 获取函数名称用于日志记录
            func_name = func.__name__
            
            for attempt in range(1, max_attempts + 1):
                try:
                    log.info(f"执行 {func_name} (尝试 {attempt}/{max_attempts})")
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    last_exception = e
                    log.warning(f"{func_name} 失败 (尝试 {attempt}/{max_attempts}): {str(e)}")
                    
                    # 最后一次尝试失败后，不再等待
                    if attempt < max_attempts:
                        log.info(f"等待 {delay} 秒后重试...")
                        time.sleep(delay)
            
            # 所有尝试都失败后，重新抛出最后一个异常
            log.error(f"{func_name} 在 {max_attempts} 次尝试后失败: {str(last_exception)}")
            raise last_exception
        return wrapper
    return decorator

class BasePage:
    """
    Base page class containing common methods for all pages
    """
    def __init__(self, device):
        """
        Initialize the base page
        
        Args:
            device (uiautomator2.Device): Connected device object
        """
        self.device = device
        self.timeout = 10
        log.info(f"初始化页面: {self.__class__.__name__}, 设备: {device.serial}")
    
    @retry(max_attempts=3)
    def find_element(self, selector, timeout=None):
        """
        Find an element using a selector
        
        Args:
            selector (dict): The selector to find the element
            timeout (int, optional): Timeout in seconds
            
        Returns:
            uiautomator2.UiObject: The found element
        """
        if timeout is None:
            timeout = self.timeout
            
        log.info(f"查找元素: {selector}, 超时: {timeout}秒")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                element = self.device(**selector)
                if element.exists:
                    log.info(f"元素已找到: {selector}")
                    return element
            except Exception as e:
                log.debug(f"查找元素时出错: {str(e)}")
            time.sleep(0.5)
            
        # 元素未找到，记录错误并截图
        error_msg = f"元素未找到: {selector}, 超时: {timeout}秒"
        log.error(error_msg)
        screenshot_util.take_screenshot(self.device, f"element_not_found_{self.__class__.__name__}")
        raise TimeoutError(error_msg)
    
    @retry(max_attempts=2)
    def click_element(self, selector, timeout=None):
        """
        Click an element using a selector
        
        Args:
            selector (dict): The selector to find the element
            timeout (int, optional): Timeout in seconds
        """
        log.info(f"点击元素: {selector}")
        try:
            element = self.find_element(selector, timeout)
            element.click()
            log.info(f"元素点击成功: {selector}")
            time.sleep(1)  # Wait for action to complete
        except Exception as e:
            log.error(f"点击元素失败: {selector}, 错误: {str(e)}")
            screenshot_util.take_screenshot(self.device, f"click_failed_{self.__class__.__name__}")
            raise
    
    @retry(max_attempts=2)
    def input_text(self, selector, text, timeout=None):
        """
        Input text to an element
        
        Args:
            selector (dict): The selector to find the element
            text (str): Text to input
            timeout (int, optional): Timeout in seconds
        """
        log.info(f"输入文本到元素: {selector}, 文本: {text}")
        try:
            element = self.find_element(selector, timeout)
            element.clear_text()
            element.send_keys(text)
            log.info(f"文本输入成功: {selector}")
            time.sleep(0.5)  # Wait for input to complete
        except Exception as e:
            log.error(f"输入文本失败: {selector}, 文本: {text}, 错误: {str(e)}")
            screenshot_util.take_screenshot(self.device, f"input_failed_{self.__class__.__name__}")
            raise
    
    def is_element_present(self, selector, timeout=5):
        """
        Check if an element is present
        
        Args:
            selector (dict): The selector to find the element
            timeout (int, optional): Timeout in seconds
            
        Returns:
            bool: True if element is present, False otherwise
        """
        log.info(f"检查元素是否存在: {selector}, 超时: {timeout}秒")
        try:
            self.find_element(selector, timeout)
            log.info(f"元素存在: {selector}")
            return True
        except (TimeoutError, Exception) as e:
            log.info(f"元素不存在: {selector}, 原因: {str(e)}")
            return False
    
    def wait_for_element(self, selector, timeout=None):
        """
        Wait for an element to be present
        
        Args:
            selector (dict): The selector to find the element
            timeout (int, optional): Timeout in seconds
        """
        log.info(f"等待元素出现: {selector}")
        self.find_element(selector, timeout)
        log.info(f"元素已出现: {selector}")
    
    def get_text(self, selector, timeout=None):
        """
        Get text from an element
        
        Args:
            selector (dict): The selector to find the element
            timeout (int, optional): Timeout in seconds
            
        Returns:
            str: Text of the element
        """
        log.info(f"获取元素文本: {selector}")
        try:
            element = self.find_element(selector, timeout)
            text = element.get_text()
            log.info(f"获取到文本: '{text}', 元素: {selector}")
            return text
        except Exception as e:
            log.error(f"获取文本失败: {selector}, 错误: {str(e)}")
            screenshot_util.take_screenshot(self.device, f"get_text_failed_{self.__class__.__name__}")
            raise
        
    def go_back(self):
        """
        Go back to the previous screen
        """
        log.info("返回上一页")
        self.device.press("back")
        time.sleep(1)
        log.info("返回操作完成") 