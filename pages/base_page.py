import time

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
            
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                element = self.device(**selector)
                if element.exists:
                    return element
            except Exception as e:
                print(f"Error finding element: {str(e)}")
            time.sleep(0.5)
            
        raise TimeoutError(f"Element not found with selector {selector} within {timeout} seconds")
    
    def click_element(self, selector, timeout=None):
        """
        Click an element using a selector
        
        Args:
            selector (dict): The selector to find the element
            timeout (int, optional): Timeout in seconds
        """
        element = self.find_element(selector, timeout)
        element.click()
        time.sleep(1)  # Wait for action to complete
    
    def input_text(self, selector, text, timeout=None):
        """
        Input text to an element
        
        Args:
            selector (dict): The selector to find the element
            text (str): Text to input
            timeout (int, optional): Timeout in seconds
        """
        element = self.find_element(selector, timeout)
        element.clear_text()
        element.send_keys(text)
        time.sleep(0.5)  # Wait for input to complete
    
    def is_element_present(self, selector, timeout=5):
        """
        Check if an element is present
        
        Args:
            selector (dict): The selector to find the element
            timeout (int, optional): Timeout in seconds
            
        Returns:
            bool: True if element is present, False otherwise
        """
        try:
            self.find_element(selector, timeout)
            return True
        except (TimeoutError, Exception):
            return False
    
    def wait_for_element(self, selector, timeout=None):
        """
        Wait for an element to be present
        
        Args:
            selector (dict): The selector to find the element
            timeout (int, optional): Timeout in seconds
        """
        self.find_element(selector, timeout)
    
    def get_text(self, selector, timeout=None):
        """
        Get text from an element
        
        Args:
            selector (dict): The selector to find the element
            timeout (int, optional): Timeout in seconds
            
        Returns:
            str: Text of the element
        """
        element = self.find_element(selector, timeout)
        return element.get_text()
        
    def go_back(self):
        """
        Go back to the previous screen
        """
        self.device.press("back")
        time.sleep(1) 