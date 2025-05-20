import os
import yaml

def load_yaml(file_path):
    """
    Load data from a YAML file
    
    Args:
        file_path (str): Path to the YAML file
        
    Returns:
        dict: The loaded YAML data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find YAML file at {file_path}")
    
    with open(file_path, 'r') as yaml_file:
        return yaml.safe_load(yaml_file)

def get_device_config(device_id):
    """
    Get configuration for a specific device
    
    Args:
        device_id (str): The ID of the device
        
    Returns:
        dict: Device configuration
    """
    devices_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'devices.yaml')
    devices_data = load_yaml(devices_path)
    
    for device in devices_data.get('devices', []):
        if device.get('id') == device_id:
            return device
    
    raise ValueError(f"No configuration found for device with ID {device_id}")

def get_account_credentials(account_type):
    """
    Get account credentials by type
    
    Args:
        account_type (str): Type of account (e.g., 'valid_user')
        
    Returns:
        dict: Account credentials
    """
    credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'credentials.yaml')
    credentials_data = load_yaml(credentials_path)
    
    account = credentials_data.get('accounts', {}).get(account_type)
    if not account:
        raise ValueError(f"No credentials found for account type {account_type}")
    
    return account 