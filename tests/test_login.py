import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage
from utils.yaml_utils import get_account_credentials

class TestLogin:
    """
    Test class for login functionality
    """
    
    def test_successful_login(self, device):
        """
        Test successful login with valid credentials
        
        Args:
            device: The connected device fixture
        """
        # Get test data from credentials config
        credentials = get_account_credentials('valid_user')
        username = credentials.get('username')
        password = credentials.get('password')
        
        # Initialize page objects
        login_page = LoginPage(device)
        home_page = HomePage(device)
        
        # Perform login
        login_page.login(username, password)
        
        # Verify successful login
        assert login_page.is_login_successful(), "Login was not successful"
        
        # Verify we are on the home page
        assert home_page.is_home_page_displayed(), "Home page is not displayed after login" 