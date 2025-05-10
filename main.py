#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SofaScore Access Script with Local ChromeDriver
File name: sofascore_access.py

This script uses a locally installed ChromeDriver to access SofaScore.com
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

print("Starting SofaScore access script...")

# Setup Chrome options
chrome_options = Options()
try:
    # Initialize ChromeDriver using the local installation
    print("Setting up ChromeDriver...")
    
    # Option 1: If ChromeDriver is in your PATH
    driver = webdriver.Chrome(options=chrome_options)
    
    # Option 2: If you need to specify the ChromeDriver path
    # chromedriver_path = "/path/to/your/chromedriver"  # Update with your actual path
    # service = Service(executable_path=chromedriver_path)
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Access SofaScore website
    print("Opening SofaScore.com...")
    driver.get("https://www.sofascore.com/")
    
    # Wait for page to load
    time.sleep(3)
    
    # Print page title to confirm access
    print(f"Page title: {driver.title}")
        
    # Print confirmation message
    print("Successfully accessed SofaScore football section!")
    
    # Keep browser open until user presses Enter
    input("Press Enter to close the browser...")
    
except Exception as e:
    print(f"An error occurred: {e}")
    
finally:
    # Clean up - close the browser if it was opened
    try:
        if 'driver' in locals():
            driver.quit()
            print("Browser closed.")
    except:
        print("Could not close the browser (it might not have been opened)")