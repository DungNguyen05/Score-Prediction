#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SofaScore Access Script with Search Functionality
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def search_sofascore(search_term="Manchester United"):
    """
    Function to search for a specific term on SofaScore
    
    Args:
        search_term (str): The term to search for (default: "Manchester United")
    """
    print(f"Starting SofaScore search for '{search_term}'...")

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
        
        # Find the search box
        # Using the selector from the provided HTML snippet
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
        
        # Press Enter to submit the search
        search_box.send_keys(Keys.RETURN)
        
        # Wait for search results to load
        print("Waiting for search results...")
        time.sleep(3)
        
        # Print the current URL (should be the search results page)
        print(f"Search results URL: {driver.current_url}")
        
        # Print the title of the page
        print(f"Page title: {driver.title}")
        
        # Optional: Extract some information from the search results
        try:
            # This is an example - you may need to adjust selectors based on the actual page structure
            results = driver.find_elements(By.CSS_SELECTOR, ".search-result-item")
            print(f"Found {len(results)} search results")
            
            # Print the first few results
            for i, result in enumerate(results[:5], 1):
                print(f"Result {i}: {result.text[:100]}...")
                
        except Exception as e:
            print(f"Could not extract search results: {e}")
        
        print("Search completed successfully!")
        
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
    # Call the search function with default value "Manchester United"
    search_sofascore()
    
    # Alternatively, you can specify a different search term:
    # search_sofascore("Liverpool FC")