import sys
import os
import time
import csv
import glob
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# Thread-safe lock for writing to master CSV
csv_lock = threading.Lock()
rename_lock = threading.Lock()  # Lock for file renaming

CATEGORIES = {
    "All Categories": 0,
    "Autos and vehicles": 1,
    "Beauty and fashion": 2,
    "Business and finance": 3,
    "Climate": 20,
    "Entertainment": 4,
    "Food and drink": 5,
    "Games": 6,
    "Health": 7,
    "Hobbies and leisure": 8,
    "Jobs and education": 9,
    "Law and government": 10,
    "Other": 11,
    "Pets and animals": 13,
    "Politics": 14,
    "Science": 15,
    "Shopping": 16,
    "Sports": 17,
    "Technology": 18,
    "Travel and transportation": 19
}


def download_google_trends_csv(url, category_name, category_id, download_dir="downloads"):
    """Download CSV for a specific category with unique filename"""
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
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

    service = ChromeService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": os.path.abspath(download_dir)
    })

    downloaded_file = None
    
    try:
        print(f"[{category_name}] Opening URL...")
        existing_files = set(os.listdir(download_dir))
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        time.sleep(3)
        
        export_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Export')]")))
        export_btn.click()
        print(f"[{category_name}] Clicked Export button")

        time.sleep(2)
        csv_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Download CSV')]")
        
        if csv_element:
            try:
                parent = csv_element.find_element(By.XPATH, "./ancestor::button | ./ancestor::div[@role='menuitem'] | ./ancestor::*[@role='option']")
                driver.execute_script("arguments[0].click();", parent)
            except:
                driver.execute_script("arguments[0].click();", csv_element)
            print(f"[{category_name}] Clicked Download CSV")

        download_path = os.path.abspath(download_dir)
        max_wait = 40
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            current_files = set(os.listdir(download_path))
            new_files = current_files - existing_files
            # Filter out temp files and master files
            csv_files = [f for f in new_files if f.endswith('.csv') and not f.startswith('temp_') and not f.startswith('master_')]
            if csv_files:
                downloaded_file = csv_files[0]
                # Rename to unique filename with category_id to avoid overwriting (thread-safe)
                with rename_lock:
                    unique_name = f"category_{category_id}_{int(time.time()*1000)}_{downloaded_file}"
                    old_path = os.path.join(download_path, downloaded_file)
                    new_path = os.path.join(download_path, unique_name)
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                        downloaded_file = unique_name
                        print(f"[{category_name}] ✅ Downloaded: {downloaded_file}")
                    else:
                        print(f"[{category_name}] ⚠️ File disappeared: {downloaded_file}")
                        downloaded_file = None
                break
            time.sleep(1)
        else:
            print(f"[{category_name}] ⚠️ No CSV file detected (might be empty category)")
        
    except Exception as e:
        print(f"[{category_name}] ❌ Error: {e}")
    finally:
        driver.quit()
    
    return downloaded_file


def append_to_master_csv(csv_file, category_name, master_csv_path, download_dir="downloads"):
    """Read individual CSV and append to master CSV with category column"""
    if not csv_file:
        return False
    
    filepath = os.path.join(download_dir, csv_file)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            rows = list(reader)
        
        if len(rows) <= 1:  # Only header or empty
            print(f"[{category_name}] No data rows to add")
            return False
        
        # Thread-safe writing to master CSV
        with csv_lock:
            with open(master_csv_path, 'a', encoding='utf-8', newline='') as outfile:
                writer = csv.writer(outfile)
                
                # Add data rows with category prepended
                for i in range(1, len(rows)):
                    row_with_category = [category_name] + rows[i]
                    writer.writerow(row_with_category)
        
        print(f"[{category_name}] ✅ Added {len(rows)-1} rows to master CSV")
        return True
        
    except Exception as e:
        print(f"[{category_name}] ❌ Error appending to master: {e}")
        return False


def create_master_csv(master_csv_path, download_dir="downloads"):
    """Create master CSV file with headers"""
    os.makedirs(download_dir, exist_ok=True)
    
    # Standard Google Trends CSV headers with Category prepended
    headers = [
        "Category",
        "Trends",
        "Search volume",
        "Started",
        "Ended",
        "Trend breakdown",
        "Explore link"
    ]
    
    try:
        with open(master_csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        print(f"✅ Created master CSV: {master_csv_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating master CSV: {e}")
        return False


def download_category(category_name, category_id, geo, download_dir, master_csv_path):
    """Download and process a single category, appending to master CSV"""
    import random
    time.sleep(random.uniform(1, 3))
    
    url = f"https://trends.google.com/trending?geo={geo}&category={category_id}"
    csv_file = download_google_trends_csv(url, category_name, category_id, download_dir)
    
    if csv_file:
        success = append_to_master_csv(csv_file, category_name, master_csv_path, download_dir)
        return success
    return False


def download_all_categories(geo="IN", download_dir="downloads", max_workers=3):
    """Download CSV for all categories in parallel and append to master CSV"""
    print(f"🚀 Starting parallel download for {len(CATEGORIES)} categories...")
    print(f"   Using {max_workers} parallel workers")
    print("=" * 70)
    
    # Create master CSV file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    master_csv_filename = f"master_trends_{geo}_{timestamp}.csv"
    master_csv_path = os.path.join(download_dir, master_csv_filename)
    
    if not create_master_csv(master_csv_path, download_dir):
        print("❌ Failed to create master CSV. Aborting.")
        return None
    
    print(f"📝 Master CSV: {master_csv_filename}")
    print("=" * 70)
    
    successful_count = 0
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_category = {
            executor.submit(download_category, cat_name, cat_id, geo, download_dir, master_csv_path): cat_name
            for cat_name, cat_id in CATEGORIES.items()
        }
        
        for future in as_completed(future_to_category):
            category_name = future_to_category[future]
            try:
                success = future.result()
                if success:
                    successful_count += 1
            except Exception as e:
                print(f"[{category_name}] Exception: {e}")
    
    elapsed_time = time.time() - start_time
    print("=" * 70)
    print(f"✅ Successfully processed {successful_count} out of {len(CATEGORIES)} categories")
    print(f"⏱️  Total time: {elapsed_time:.2f} seconds")
    print(f"📄 Final CSV: {master_csv_path}")
    
    # Count total rows in master CSV
    try:
        with open(master_csv_path, 'r', encoding='utf-8') as f:
            row_count = sum(1 for line in f) - 1  # Exclude header
        print(f"📊 Total data rows: {row_count}")
    except:
        pass
    
    return master_csv_path


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1].startswith("http"):
            # Single URL mode - extract category from URL or use "Manual"
            url = sys.argv[1]
            category_name = "Manual"
            category_id = 0
            
            # Try to extract category from URL
            if "category=" in url:
                try:
                    category_id = int(url.split("category=")[1].split("&")[0])
                    # Find category name
                    for name, cid in CATEGORIES.items():
                        if cid == category_id:
                            category_name = name
                            break
                except:
                    pass
            
            csv_file = download_google_trends_csv(url, category_name, category_id, "downloads")
            if csv_file:
                print(f"\n✅ Downloaded: downloads/{csv_file}")
        elif sys.argv[1] == "all":
            geo = sys.argv[2] if len(sys.argv) > 2 else "IN"
            workers = int(sys.argv[3]) if len(sys.argv) > 3 else 3
            download_all_categories(geo=geo, max_workers=workers)
        else:
            print("Usage:")
            print("  python google.py <URL>                   # Single URL")
            print("  python google.py all [GEO] [WORKERS]    # All categories")
            print("\nExamples:")
            print("  python google.py all IN 5")
            print('  python google.py "https://trends.google.com/trending?geo=IN&category=3"')
    else:
        download_all_categories(geo="IN", max_workers=3)
