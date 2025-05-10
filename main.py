#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SofaScore Search and Click Function
This script searches for "Manchester United" on SofaScore and clicks the first result
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def search_and_click_first_result(search_term="Manchester United"):
    """
    Function to search for a term on SofaScore and click the first result
    
    Args:
        search_term (str): The term to search for (default: "Manchester United")
    """
    print(f"Starting SofaScore search for '{search_term}' and clicking first result...")

    # Setup Chrome options
    chrome_options = Options()
    driver = None
    
    try:
        # Initialize ChromeDriver
        print("Setting up ChromeDriver...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Access SofaScore website
        print("Opening SofaScore.com...")
        driver.get("https://www.sofascore.com/")
        
        # Wait for page to load
        print("Waiting for page to load...")
        wait = WebDriverWait(driver, 10)
        
        # Find the search box using the selector from the provided HTML
        search_box = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input.sc-23fa27a7-0.hJrmWL")
        ))
        
        # Alternative selectors if the above doesn't work
        # search_box = wait.until(EC.presence_of_element_located((By.ID, "search-input")))
        # search_box = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search matches, competitions, teams, players, and more']")))
        
        print(f"Found search box, entering '{search_term}'...")
        
        # Clear any existing text and enter search term
        search_box.clear()
        search_box.send_keys(search_term)
        
        # Wait for search results to appear
        # Based on your HTML, the search results appear in a dropdown, not after page navigation
        print("Waiting for search results dropdown...")
        time.sleep(2)  # Short wait for the dropdown to appear
        
        # Find the first <a> tag in the search results
        # Using the structure from your HTML snippet
        first_result_link = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.beautiful-scrollbar__content a.sc-5bbe3e2c-0")
        ))
        
        # Print information about what we're clicking
        print(f"Found first result: {first_result_link.text}")
        print(f"Clicking on the first search result (Manchester United team)...")
        
        # Click on the first result
        first_result_link.click()
        
        # Wait for the team page to load
        print("Waiting for team page to load...")
        time.sleep(3)
        
        # Print confirmation
        print(f"Successfully navigated to: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Keep browser open until user presses Enter
        input("Press Enter to close the browser...")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Clean up - close the browser if it was opened
        try:
            if driver:
                driver.quit()
                print("Browser closed.")
        except:
            print("Could not close the browser (it might not have been opened)")


if __name__ == "__main__":
    # Call the function to search and click the first result
    search_and_click_first_result()