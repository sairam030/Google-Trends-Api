"""Test the deployed API to see detailed error information"""
import requests
import json

BASE_URL = "https://google-trends-api-production-560a.up.railway.app"

print("=" * 70)
print("Testing Deployed Google Trends API")
print("=" * 70)

# Test 1: Health check
print("\n1. Health Check:")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Categories
print("\n2. Categories:")
try:
    response = requests.get(f"{BASE_URL}/categories")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total: {data.get('total')}")
    print(f"   First 3 categories:")
    for cat in data.get('categories', [])[:3]:
        print(f"      - {cat}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Sports category (known to have data)
print("\n3. Testing Sports Category (IN):")
try:
    response = requests.get(f"{BASE_URL}/api/v1/IN/sports")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Technology category
print("\n4. Testing Technology Category (IN):")
try:
    response = requests.get(f"{BASE_URL}/api/v1/IN/technology")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("The issue: API returns 404 'No trends found' but data exists on website")
print("Next step: Check Railway logs for Selenium/Chrome errors")
print("=" * 70)
