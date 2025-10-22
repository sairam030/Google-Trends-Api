# Demo script to test download a few categories and merge
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from google import download_category, merge_csv_files, CATEGORIES
from datetime import datetime

# Select just 3 categories for demo
demo_categories = {
    "Business and finance": 3,
    "Entertainment": 5,
    "Technology": 18
}

print("🔥 DEMO: Downloading 3 categories...")
print("=" * 60)

downloaded = []
for cat_name, cat_id in demo_categories.items():
    result = download_category(cat_name, cat_id, "IN", "downloads")
    if result:
        downloaded.append(result)
        print(f"✅ {cat_name}: SUCCESS\n")
    else:
        print(f"❌ {cat_name}: FAILED\n")

print("=" * 60)
print(f"\n📊 Downloaded {len(downloaded)}/{len(demo_categories)} categories\n")

# Merge files
if downloaded:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged = merge_csv_files("downloads", f"demo_merged_{timestamp}.csv")
    if merged:
        print(f"\n✨ SUCCESS! Check {merged}")
        # Show sample
        import csv
        with open(merged, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            print(f"\n📋 Sample (first 5 rows):")
            for row in rows[:5]:
                print(row[:3])  # Show first 3 columns
