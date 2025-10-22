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
    """Download CSV for a specific category and save with category-specific filename"""
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
        print(f"\n[{category_name}] Opening URL...")
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
        
        # Wait for the download to complete
        while time.time() - start_time < max_wait:
            current_files = set(os.listdir(download_path))
            new_files = current_files - existing_files
            # Filter out temp files and previous category files
            csv_files = [f for f in new_files if f.endswith('.csv') and not f.startswith('temp_') and not f.startswith('merged_')]
            if csv_files:
                downloaded_file = csv_files[0]
                
                # Create category-specific filename
                safe_category_name = category_name.replace(" ", "_").replace("&", "and")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_name = f"{safe_category_name}_cat{category_id}_{timestamp}.csv"
                
                old_path = os.path.join(download_path, downloaded_file)
                new_path = os.path.join(download_path, unique_name)
                
                # Wait a bit to ensure file is fully written
                time.sleep(1)
                
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    downloaded_file = unique_name
                    print(f"[{category_name}] ✅ Saved as: {downloaded_file}")
                else:
                    print(f"[{category_name}] ⚠️ File not found: {downloaded_file}")
                    downloaded_file = None
                break
            time.sleep(1)
        else:
            print(f"[{category_name}] ⚠️ No CSV file detected (might be empty category)")
        
    except Exception as e:
        print(f"[{category_name}] ❌ Error: {e}")
        downloaded_file = None
    finally:
        driver.quit()
    
    return downloaded_file


def add_category_column(csv_file, category_name, download_dir="downloads"):
    """Add category column to a CSV file"""
    if not csv_file:
        return None
    
    filepath = os.path.join(download_dir, csv_file)
    
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            rows = list(reader)
        
        if len(rows) == 0:
            print(f"[{category_name}] Empty file, skipping")
            return None
        
        # Add Category as first column in header
        if len(rows) > 0:
            rows[0].insert(0, "Category")
            
            # Add category name to all data rows
            for i in range(1, len(rows)):
                rows[i].insert(0, category_name)
        
        # Write back to the same file
        with open(filepath, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(rows)
        
        print(f"[{category_name}] ✅ Added category column ({len(rows)-1} data rows)")
        return filepath
        
    except Exception as e:
        print(f"[{category_name}] ❌ Error adding category column: {e}")
        return None


def merge_all_category_files(download_dir="downloads"):
    """Merge all category CSV files into one master file"""
    print("\n" + "=" * 70)
    print("📦 Starting merge process...")
    
    # Find all category files (exclude merged files)
    csv_files = glob.glob(os.path.join(download_dir, "*_cat*.csv"))
    csv_files = [f for f in csv_files if not os.path.basename(f).startswith("merged_")]
    
    if not csv_files:
        print("❌ No category CSV files found to merge")
        return None
    
    print(f"   Found {len(csv_files)} category files")
    
    # Sort files by category ID for consistent ordering
    csv_files.sort()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_filename = f"merged_trends_{timestamp}.csv"
    merged_path = os.path.join(download_dir, merged_filename)
    
    all_rows = []
    header = None
    total_data_rows = 0
    
    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
                if len(rows) > 0:
                    if header is None:
                        # Use first file's header
                        header = rows[0]
                        all_rows.append(header)
                    
                    # Add data rows (skip header)
                    data_rows = rows[1:]
                    all_rows.extend(data_rows)
                    total_data_rows += len(data_rows)
                    
                    category_name = os.path.basename(csv_file).split('_cat')[0].replace('_', ' ')
                    print(f"   ✅ {category_name}: {len(data_rows)} rows")
                    
        except Exception as e:
            print(f"   ❌ Error reading {os.path.basename(csv_file)}: {e}")
    
    # Write merged file
    try:
        with open(merged_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(all_rows)
        
        print("=" * 70)
        print(f"✅ Merged file created: {merged_filename}")
        print(f"   Total data rows: {total_data_rows}")
        print(f"   Full path: {merged_path}")
        return merged_path
        
    except Exception as e:
        print(f"❌ Error writing merged file: {e}")
        return None


def download_all_categories_sequential(geo="IN", download_dir="downloads"):
    """Download CSV for all categories one by one (sequential), then merge"""
    print("🚀 Starting SEQUENTIAL download for all categories")
    print(f"   Total categories: {len(CATEGORIES)}")
    print(f"   Geography: {geo}")
    print("=" * 70)
    
    successful_files = []
    failed_categories = []
    empty_categories = []
    
    start_time = time.time()
    
    for idx, (category_name, category_id) in enumerate(CATEGORIES.items(), 1):
        print(f"\n[{idx}/{len(CATEGORIES)}] Processing: {category_name} (ID: {category_id})")
        
        url = f"https://trends.google.com/trending?geo={geo}&category={category_id}"
        
        # Download the CSV
        csv_file = download_google_trends_csv(url, category_name, category_id, download_dir)
        
        if csv_file:
            # Add category column
            processed_file = add_category_column(csv_file, category_name, download_dir)
            
            if processed_file:
                successful_files.append(processed_file)
            else:
                empty_categories.append(category_name)
        else:
            failed_categories.append(category_name)
        
        # Small delay between categories to avoid overwhelming the server
        if idx < len(CATEGORIES):
            print(f"   Waiting 2 seconds before next category...")
            time.sleep(2)
    
    elapsed_time = time.time() - start_time
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 70)
    print(f"✅ Successful: {len(successful_files)}")
    print(f"ℹ️  Empty: {len(empty_categories)}")
    print(f"❌ Failed: {len(failed_categories)}")
    print(f"⏱️  Total time: {elapsed_time:.2f} seconds")
    
    if empty_categories:
        print(f"\nℹ️  Empty categories: {', '.join(empty_categories)}")
    
    if failed_categories:
        print(f"\n❌ Failed categories: {', '.join(failed_categories)}")
    
    # Merge all successful files
    if successful_files:
        merged_file = merge_all_category_files(download_dir)
        return merged_file
    else:
        print("\n❌ No files to merge")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1].startswith("http"):
            # Single URL mode
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
                processed = add_category_column(csv_file, category_name, "downloads")
                if processed:
                    print(f"\n✅ File saved: downloads/{csv_file}")
        
        elif sys.argv[1] == "all":
            geo = sys.argv[2] if len(sys.argv) > 2 else "IN"
            download_all_categories_sequential(geo=geo)
        
        else:
            print("Usage:")
            print("  python google_sequential.py <URL>       # Single URL")
            print("  python google_sequential.py all [GEO]  # All categories (sequential)")
            print("\nExamples:")
            print("  python google_sequential.py all IN")
            print('  python google_sequential.py "https://trends.google.com/trending?geo=IN&category=3"')
    else:
        download_all_categories_sequential(geo="IN")
