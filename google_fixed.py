import sys
import os
import time
import csv
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

CATEGORIES = {
    "All_Categories": 0,
    "Autos_and_vehicles": 1,
    "Beauty_and_fashion": 2,
    "Business_and_finance": 3,
    "Climate": 4,
    "Entertainment": 5,
    "Food_and_drink": 6,
    "Games": 7,
    "Health": 8,
    "Hobbies_and_leisure": 9,
    "Jobs_and_education": 10,
    "Law_and_government": 11,
    "Other": 12,
    "Pets_and_animals": 13,
    "Politics": 14,
    "Science": 15,
    "Shopping": 16,
    "Sports": 17,
    "Technology": 18,
    "Travel_and_transportation": 19
}


def download_google_trends_csv(url, category_name, category_id, download_dir="downloads"):
    """Download CSV for specific category and save with category-based filename"""
    os.makedirs(download_dir, exist_ok=True)

    # Create unique filename based on category name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # milliseconds
    final_filename = f"{category_name}_cat{category_id}_{timestamp}.csv"
    final_path = os.path.abspath(os.path.join(download_dir, final_filename))

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

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
        print(f"[{category_name}] Clicked Export")

        time.sleep(2)
        csv_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Download CSV')]")
        
        if csv_element:
            try:
                parent = csv_element.find_element(By.XPATH, "./ancestor::button | ./ancestor::div[@role='menuitem'] | ./ancestor::*[@role='option']")
                driver.execute_script("arguments[0].click();", parent)
            except:
                driver.execute_script("arguments[0].click();", csv_element)
            print(f"[{category_name}] Clicked Download CSV")

        # Wait for download
        download_path = os.path.abspath(download_dir)
        max_wait = 40
        start_time = time.time()
        
        temp_file = None
        while time.time() - start_time < max_wait:
            current_files = set(os.listdir(download_path))
            new_files = current_files - existing_files
            csv_files = [f for f in new_files if f.endswith('.csv') and not f.startswith(category_name) and not f.startswith('master_')]
            if csv_files:
                temp_file = csv_files[0]
                break
            time.sleep(1)
        
        if temp_file:
            temp_path = os.path.join(download_path, temp_file)
            if os.path.exists(temp_path):
                os.rename(temp_path, final_path)
                downloaded_file = final_filename
                print(f"[{category_name}] ✅ Saved as: {downloaded_file}")
            else:
                print(f"[{category_name}] ⚠️ File disappeared")
        else:
            print(f"[{category_name}] ⚠️ No data (empty category)")
        
    except Exception as e:
        print(f"[{category_name}] ❌ Error: {str(e)[:100]}")
    finally:
        driver.quit()
    
    return downloaded_file


def append_to_master_csv(csv_file, category_name, master_csv_path, download_dir="downloads"):
    """Read category CSV and append to master with category column"""
    if not csv_file:
        return False
    
    filepath = os.path.join(download_dir, csv_file)
    
    if not os.path.exists(filepath):
        print(f"[{category_name}] ❌ File not found: {csv_file}")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            rows = list(reader)
        
        if len(rows) <= 1:
            print(f"[{category_name}] ℹ️ No data rows")
            return False
        
        # Thread-safe writing to master CSV
        with csv_lock:
            with open(master_csv_path, 'a', encoding='utf-8', newline='') as outfile:
                writer = csv.writer(outfile)
                
                # Add data rows with category prepended
                data_rows = 0
                for i in range(1, len(rows)):
                    row_with_category = [category_name.replace("_", " ")] + rows[i]
                    writer.writerow(row_with_category)
                    data_rows += 1
        
        print(f"[{category_name}] ✅ Added {data_rows} rows to master CSV")
        return True
        
    except Exception as e:
        print(f"[{category_name}] ❌ Error appending: {str(e)[:100]}")
        return False


def create_master_csv(master_csv_path, download_dir="downloads"):
    """Create master CSV file with headers"""
    os.makedirs(download_dir, exist_ok=True)
    
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
        print(f"✅ Created master CSV: {master_csv_path}\n")
        return True
    except Exception as e:
        print(f"❌ Error creating master CSV: {e}")
        return False


def download_category(category_name, category_id, geo, download_dir, master_csv_path):
    """Download and process single category"""
    import random
    time.sleep(random.uniform(1, 3))
    
    url = f"https://trends.google.com/trending?geo={geo}&category={category_id}"
    csv_file = download_google_trends_csv(url, category_name, category_id, download_dir)
    
    if csv_file:
        success = append_to_master_csv(csv_file, category_name, master_csv_path, download_dir)
        return {"success": success, "file": csv_file, "category": category_name}
    
    return {"success": False, "file": None, "category": category_name}


def download_all_categories(geo="IN", download_dir="downloads", max_workers=3):
    """Download all categories in parallel and create master CSV"""
    print(f"\n🚀 GOOGLE TRENDS DOWNLOADER")
    print(f"   Categories: {len(CATEGORIES)}")
    print(f"   Parallel workers: {max_workers}")
    print(f"   Country: {geo}")
    print("=" * 70)
    
    # Create master CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    master_csv_filename = f"master_trends_{geo}_{timestamp}.csv"
    master_csv_path = os.path.join(download_dir, master_csv_filename)
    
    if not create_master_csv(master_csv_path, download_dir):
        print("❌ Failed to create master CSV. Aborting.")
        return None
    
    successful = []
    failed = []
    empty = []
    errors = []
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_category = {
            executor.submit(download_category, cat_name, cat_id, geo, download_dir, master_csv_path): cat_name
            for cat_name, cat_id in CATEGORIES.items()
        }
        
        for future in as_completed(future_to_category):
            category_name = future_to_category[future]
            try:
                result = future.result()
                if result["success"]:
                    successful.append(result)
                elif result["file"]:
                    empty.append(result)
                else:
                    failed.append(result)
            except Exception as e:
                errors.append({"category": category_name, "error": str(e)[:100]})
                print(f"[{category_name}] 💥 Exception: {str(e)[:100]}")
    
    elapsed_time = time.time() - start_time
    
    # Summary
    print("\n" + "=" * 70)
    print(f"📊 SUMMARY")
    print(f"   ✅ Success: {len(successful)}")
    print(f"   ℹ️  Empty: {len(empty)}")
    print(f"   ❌ Failed: {len(failed)}")
    if errors:
        print(f"   💥 Errors: {len(errors)}")
    print(f"   ⏱️  Time: {elapsed_time:.1f}s")
    print("=" * 70)
    
    if errors:
        print(f"\n⚠️  ERRORS ENCOUNTERED:")
        for err in errors:
            print(f"   • {err['category']}: {err['error']}")
    
    # Count rows
    try:
        with open(master_csv_path, 'r', encoding='utf-8') as f:
            row_count = sum(1 for line in f) - 1
        print(f"\n📄 Master CSV: {master_csv_filename}")
        print(f"📊 Total data rows: {row_count}")
        
        if successful:
            print(f"\n✅ Category files saved:")
            for s in successful[:10]:  # Show first 10
                print(f"   • {s['file']}")
            if len(successful) > 10:
                print(f"   ... and {len(successful) - 10} more")
    except:
        pass
    
    return master_csv_path


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        geo = sys.argv[2] if len(sys.argv) > 2 else "IN"
        workers = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        download_all_categories(geo=geo, max_workers=workers)
    else:
        print("Usage: python google_fixed.py all [GEO] [WORKERS]")
        print("Example: python google_fixed.py all IN 3")
