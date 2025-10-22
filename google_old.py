import sys
import os
import time
import csv
import glob
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

CATEGORIES = {
    "All Categories": 0,
    "Autos and vehicles": 1,
    "Beauty and fashion": 2,
    "Business and finance": 3,
    "Climate": 4,
    "Entertainment": 5,
    "Food and drink": 6,
    "Games": 7,
    "Health": 8,
    "Hobbies and leisure": 9,
    "Jobs and education": 10,
    "Law and government": 11,
    "Other": 12,
    "Pets and animals": 13,
    "Politics": 14,
    "Science": 15,
    "Shopping": 16,
    "Sports": 17,
    "Technology": 18,
    "Travel and transportation": 19
}

def download_google_trends_csv(url, category_name, download_dir="downloads"):
    """Download CSV for a specific category"""
    # Create download folder
    os.makedirs(download_dir, exist_ok=True)

    # Chrome options (fixed for Linux)
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # use new headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-software-rasterizer")

    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Initialize driver safely - using Chromium for snap installations
    service = ChromeService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Enable downloads in headless mode
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": os.path.abspath(download_dir)
    })

    downloaded_file = None
    
    try:
        print(f"[{category_name}] Opening: {url}")
        
        # Get list of existing files before download
        existing_files = set(os.listdir(download_dir))
        
        driver.get(url)

        # Wait for page to load completely
        wait = WebDriverWait(driver, 20)
        time.sleep(3)
        
        # Wait for Export button and click it
        export_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Export')]")))
        export_btn.click()
        print(f"[{category_name}] Clicked Export button")

        # Wait for dropdown menu to appear and become stable
        time.sleep(2)
        
        # Print all clickable elements for debugging
        print(f"[{category_name}] Looking for Download CSV option...")
        
        # Try to find the Download CSV element
        time.sleep(1)
        csv_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Download CSV')]")
        
        if csv_element:
            print(f"[{category_name}] Found element")
            
            # Try clicking the parent button/div instead
            try:
                parent = csv_element.find_element(By.XPATH, "./ancestor::button | ./ancestor::div[@role='menuitem'] | ./ancestor::*[@role='option']")
                driver.execute_script("arguments[0].click();", parent)
                print(f"[{category_name}] Clicked Download CSV using JavaScript")
            except:
                # Fallback: try clicking with JavaScript directly
                driver.execute_script("arguments[0].click();", csv_element)
                print(f"[{category_name}] Clicked Download CSV using JavaScript")
        else:
            print(f"[{category_name}] Could not find Download CSV element")

        # Wait for download to complete by checking for new files
        print(f"[{category_name}] Waiting for file to download...")
        download_path = os.path.abspath(download_dir)
        max_wait = 30  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            current_files = set(os.listdir(download_path))
            new_files = current_files - existing_files
            csv_files = [f for f in new_files if f.endswith('.csv')]
            if csv_files:
                downloaded_file = csv_files[0]
                print(f"[{category_name}] ✅ CSV file downloaded: {downloaded_file}")
                break
            time.sleep(1)
        else:
            print(f"[{category_name}] ⚠️ Warning: No CSV file detected")
        
    except Exception as e:
        print(f"[{category_name}] ❌ Error:", e)
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
    
    return downloaded_file
    # Create download folder
    os.makedirs(download_dir, exist_ok=True)

    # Chrome options (fixed for Linux)
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # use new headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-software-rasterizer")

    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Initialize driver safely - using Chromium for snap installations
    service = ChromeService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Enable downloads in headless mode
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": os.path.abspath(download_dir)
    })

    try:
        print(f"Opening: {url}")
        driver.get(url)

        # Wait for page to load completely
        wait = WebDriverWait(driver, 20)
        time.sleep(3)
        
        # Wait for Export button and click it
        export_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Export')]")))
        export_btn.click()
        print("Clicked Export button")

        # Wait for dropdown menu to appear and become stable
        time.sleep(2)
        
        # Print all clickable elements for debugging
        print("Looking for Download CSV option...")
        
        # Try to find the Download CSV element
        time.sleep(1)
        csv_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Download CSV')]")
        
        if csv_element:
            print(f"Found element: {csv_element.text}")
            
            # Try clicking the parent button/div instead
            try:
                parent = csv_element.find_element(By.XPATH, "./ancestor::button | ./ancestor::div[@role='menuitem'] | ./ancestor::*[@role='option']")
                print(f"Clicking parent element: {parent.tag_name}")
                driver.execute_script("arguments[0].click();", parent)
                print("Clicked Download CSV using JavaScript")
            except:
                # Fallback: try clicking with JavaScript directly
                print("Trying direct JavaScript click...")
                driver.execute_script("arguments[0].click();", csv_element)
                print("Clicked Download CSV using JavaScript")
        else:
            print("Could not find Download CSV element")
            driver.save_screenshot("debug_screenshot.png")

        # Wait for download to complete by checking for new files
        print("Waiting for file to download...")
        download_path = os.path.abspath(download_dir)
        max_wait = 30  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            files = os.listdir(download_path)
            csv_files = [f for f in files if f.endswith('.csv')]
            if csv_files:
                print(f"✅ CSV file downloaded: {csv_files[0]}")
                break
            time.sleep(1)
        else:
            print("⚠️ Warning: No CSV file detected in downloads folder")
        
        print(f"Download folder: {download_path}")

    except Exception as e:
        print("❌ Error:", e)
        import traceback
        traceback.print_exc()
        # Save screenshot for debugging
        try:
            driver.save_screenshot("error_screenshot.png")
            print("Error screenshot saved as error_screenshot.png")
        except:
            pass
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python google.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    download_google_trends_csv(url)
