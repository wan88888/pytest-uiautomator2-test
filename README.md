# Android UI Automation Testing Framework

A pytest-based automation testing framework for Android applications using uiautomator2.

## Features

- Page Object Model (POM) architecture
- Parallel test execution on multiple Android devices
- YAML configuration for devices and test credentials
- Combined HTML test reports with accurate test durations
- Error handling with retry mechanism
- Automatic screenshots on test failures
- Easy to extend and maintain

## Prerequisites

- Python 3.6+
- Android devices or emulators with Developer Options enabled
- Android Debug Bridge (ADB) installed and configured
- Swag Labs Sample App installed on the test devices

## Installation

1. Clone the repository
2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Install uiautomator2 on your Android devices:
   ```
   python -m uiautomator2 init
   ```

## Configuration

### Device Configuration

Edit `config/devices.yaml` to configure your Android devices:

```yaml
devices:
  - id: "device1"
    serial: "R9WR10F2QQJ"  # Device serial number (from adb devices)
    platform_version: "11"
    app_package: "com.swaglabsmobileapp"
    app_activity: "com.swaglabsmobileapp.MainActivity"
    
  - id: "device2"
    serial: "ZL5227R9TD"
    platform_version: "10"
    app_package: "com.swaglabsmobileapp"
    app_activity: "com.swaglabsmobileapp.MainActivity"
```

### Credentials Configuration

Edit `config/credentials.yaml` to configure the test accounts:

```yaml
accounts:
  valid_user:
    username: "standard_user"
    password: "secret_sauce"
  invalid_user:
    username: "invalid@example.com"
    password: "wrongpassword"
```

## Running Tests

### Run Tests on All Configured Devices in Parallel

```
python run_parallel_tests.py
```

This command will:
1. Run tests in parallel on all devices configured in devices.yaml
2. Generate a combined HTML report with results from all devices
3. The report will show test durations, outcomes, and other details

### Run Tests on a Specific Device

```
pytest tests/test_login.py --device-id=device1 -v
```

### Run a Specific Test

```
pytest tests/test_login.py::TestLogin::test_successful_login --device-id=device1 -v
```

### Test Reports

A combined HTML test report is automatically generated in the `reports` directory when running tests in parallel. The report includes results from all devices, with test durations, pass/fail status, and summary statistics.

```
reports/combined_report_YYYYMMDD_HHMMSS.html
```

To generate a test report when running a test manually:

```
pytest tests/test_login.py --device-id=device1 -v --html=reports/report.html --self-contained-html
```

## Project Structure

```
├── config/                   # Configuration files
│   ├── credentials.yaml      # Test account credentials
│   └── devices.yaml          # Device configurations
├── pages/                    # Page Object Model classes
│   ├── base_page.py          # Base page with common methods
│   ├── home_page.py          # Home page implementation
│   └── login_page.py         # Login page implementation
├── reports/                  # Test reports directory
├── screenshots/              # Screenshots taken on test failures
├── temp/                     # Temporary test result files
├── tests/                    # Test cases
│   └── test_login.py         # Login test cases
├── utils/                    # Utility modules
│   ├── device_manager.py     # Device management utilities
│   ├── logger.py             # Logging configuration
│   ├── screenshot_util.py    # Screenshot utilities
│   └── yaml_utils.py         # YAML loading utilities
├── conftest.py               # pytest configuration and fixtures
├── requirements.txt          # Python dependencies
└── run_parallel_tests.py     # Script to run tests in parallel
```

## Extending the Framework

### Adding New Page Objects

1. Create a new file in the `pages` directory
2. Extend the `BasePage` class
3. Define element selectors and page methods

### Adding New Test Cases

1. Create a new test file in the `tests` directory
2. Use the `device` fixture to get access to the connected device
3. Use page objects to interact with the application

## Troubleshooting

- Ensure ADB can detect your devices using `adb devices`
- Make sure the Swag Labs Sample App is installed on your devices
- Check device serial numbers in `config/devices.yaml` match the output of `adb devices`
- Verify the application package and activity names are correct
- If test durations show as 0.00 in reports, ensure you're using pytest-json-report 