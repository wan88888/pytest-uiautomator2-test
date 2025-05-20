from pages.base_page import BasePage
import time

class LoginPage(BasePage):
    """
    Login page class for Swag Labs App
    """
    
    # Element selectors
    USERNAME_FIELD = {"description": "test-Username"}
    PASSWORD_FIELD = {"description": "test-Password"}
    LOGIN_BUTTON = {"description": "test-LOGIN"}
    LOGIN_FORM = {"description": "test-Login"}
    ERROR_MESSAGE = {"description": "test-Error message"}
    PRODUCTS_TITLE = {"text": "PRODUCTS"}
    
    def __init__(self, device):
        """
        Initialize the login page
        
        Args:
            device (uiautomator2.Device): Connected device object
        """
        super().__init__(device)
    
    def navigate_to_login(self):
        """
        Navigate to the login page from the main screen
        """
        # For the Swag Labs app, we are already on the login page when app starts
        # So no navigation is needed
        time.sleep(1)
    
    def enter_username(self, username):
        """
        Enter the username
        
        Args:
            username (str): Username to enter
        """
        self.input_text(self.USERNAME_FIELD, username)
    
    def enter_password(self, password):
        """
        Enter the password
        
        Args:
            password (str): Password to enter
        """
        self.input_text(self.PASSWORD_FIELD, password)
    
    def click_login(self):
        """
        Click the login button
        """
        self.click_element(self.LOGIN_BUTTON)
        time.sleep(2)  # Wait for login process
    
    def login(self, username, password):
        """
        Perform the login action with given credentials
        
        Args:
            username (str): Username to enter
            password (str): Password to enter
        """
        self.navigate_to_login()
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
    
    def is_login_successful(self):
        """
        Check if login was successful
        
        Returns:
            bool: True if login was successful, False otherwise
        """
        # In Swag Labs app, successful login shows the PRODUCTS title
        return self.is_element_present(self.PRODUCTS_TITLE, timeout=5)
    
    def is_login_page_displayed(self):
        """
        Check if the login page is displayed
        
        Returns:
            bool: True if login page is displayed, False otherwise
        """
        return self.is_element_present(self.LOGIN_FORM, timeout=5)
    
    def get_error_message(self):
        """
        Get the error message if login failed
        
        Returns:
            str: Error message text or empty string if no error
        """
        if self.is_element_present(self.ERROR_MESSAGE, timeout=3):
            return self.get_text(self.ERROR_MESSAGE)
        return "" 