"""Test the scraping function locally"""
import sys
sys.path.insert(0, 'src')

from main import scrape_google_trends

print("=" * 70)
print("Testing Google Trends Scraping Locally")
print("=" * 70)

# Test sports category for India
url = "https://trends.google.com/trending?geo=IN&category=17"
category_name = "Sports"
category_id = 17

print(f"\nURL: {url}")
print(f"Category: {category_name}")
print(f"\nStarting scrape...")
print("-" * 70)

try:
    result = scrape_google_trends(url, category_name, category_id)
    
    if result:
        print(f"\n✅ SUCCESS! Found {len(result)} trends")
        print("\nFirst 3 trends:")
        for i, trend in enumerate(result[:3], 1):
            print(f"\n{i}. {trend.get('trends', 'N/A')}")
            print(f"   Search Volume: {trend.get('search_volume', 'N/A')}")
            print(f"   Started: {trend.get('started', 'N/A')}")
    else:
        print("\n❌ FAILED: No data returned (result is None)")
        print("This is the same error happening on Railway!")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
