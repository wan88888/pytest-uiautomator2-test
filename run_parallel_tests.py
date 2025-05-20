#!/usr/bin/env python
"""
Script to run tests in parallel on multiple Android devices
"""

import sys
from conftest import run_tests_in_parallel

if __name__ == "__main__":
    # Get the test module from command line argument or use default
    if len(sys.argv) > 1:
        test_module = sys.argv[1]
    else:
        test_module = "tests/test_login.py"
        
    print(f"Running tests in parallel on all configured devices: {test_module}")
    run_tests_in_parallel(test_module) 