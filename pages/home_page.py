from pages.base_page import BasePage
import time

class HomePage(BasePage):
    """
    Home page class for Swag Labs App
    """
    
    # Element selectors
    PRODUCTS_TITLE = {"text": "PRODUCTS"}
    INVENTORY_LIST = {"description": "test-INVENTORY LIST"}
    SHOPPING_CART = {"description": "test-Cart"}
    MENU_BUTTON = {"description": "test-Menu"}
    LOGOUT_BUTTON = {"description": "test-LOGOUT"}
    
    def __init__(self, device):
        """
        Initialize the home page
        
        Args:
            device (uiautomator2.Device): Connected device object
        """
        super().__init__(device)
    
    def is_home_page_displayed(self):
        """
        Check if the home page is displayed
        
        Returns:
            bool: True if home page is displayed, False otherwise
        """
        return self.is_element_present(self.PRODUCTS_TITLE, timeout=5)
    
    def get_products_title(self):
        """
        Get the products title from the home page
        
        Returns:
            str: Products title text
        """
        return self.get_text(self.PRODUCTS_TITLE)
    
    def open_cart(self):
        """
        Open the shopping cart
        """
        self.click_element(self.SHOPPING_CART)
    
    def open_menu(self):
        """
        Open the side menu
        """
        self.click_element(self.MENU_BUTTON)
    
    def logout(self):
        """
        Logout from the app
        """
        self.open_menu()
        time.sleep(1)
        self.click_element(self.LOGOUT_BUTTON)
        time.sleep(2)
    
    def select_product(self, index=0):
        """
        Select a product from the list
        
        Args:
            index (int): Index of the product to select (0-based)
        """
        # Create a dynamic selector for product items
        item_selector = {"description": f"test-Item_{index}"}
        self.click_element(item_selector) 