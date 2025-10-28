# Google Trends API - Usage Examples

## Quick Examples

### 1. Get all categories list
```bash
curl http://localhost:8000/categories
```

### 2. Get Business & Finance trends for India
```bash
curl http://localhost:8000/trends/IN/3
```

### 3. Get ALL categories for India (parallel)
```bash
curl "http://localhost:8000/trends/IN?max_workers=5"
```

### 4. Get Technology trends for USA
```bash
curl http://localhost:8000/trends/US/18
```

### 5. Pretty print JSON
```bash
curl -s http://localhost:8000/trends/IN/3 | python3 -m json.tool
```

### 6. Extract just the trend names
```bash
curl -s http://localhost:8000/trends/IN/3 | jq '.data[] | .trends'
```

### 7. Health check
```bash
curl http://localhost:8000/health
```

### 8. Clear cache
```bash
curl -X DELETE http://localhost:8000/cache
```

## Python Examples

### Basic Request
```python
import requests

response = requests.get("http://localhost:8000/trends/IN/3")
data = response.json()

print(f"Category: {data['category']}")
print(f"Total trends: {len(data['data'])}")

for trend in data['data']:
    print(f"- {trend['trends']}: {trend['search_volume']}")
```

### Get All Categories
```python
import requests

response = requests.get("http://localhost:8000/trends/IN?max_workers=5")
data = response.json()

print(f"Successfully fetched {data['successful']} categories")
print(f"Execution time: {data['execution_time']}s")

for category in data['categories']:
    print(f"\n{category['category']}:")
    for trend in category['data'][:3]:  # First 3 trends
        print(f"  - {trend['trends']}: {trend['search_volume']}")
```

### With Error Handling
```python
import requests
from requests.exceptions import RequestException

def get_trends(geo, category_id):
    try:
        response = requests.get(f"http://localhost:8000/trends/{geo}/{category_id}")
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"Error: {e}")
        return None

data = get_trends("IN", 3)
if data:
    print(f"Found {len(data['data'])} trends")
```

## JavaScript Examples

### Fetch API
```javascript
fetch('http://localhost:8000/trends/IN/3')
  .then(res => res.json())
  .then(data => {
    console.log(`Category: ${data.category}`);
    data.data.forEach(trend => {
      console.log(`${trend.trends}: ${trend.search_volume}`);
    });
  })
  .catch(err => console.error('Error:', err));
```

### Async/Await
```javascript
async function getTrends(geo, categoryId) {
  try {
    const response = await fetch(`http://localhost:8000/trends/${geo}/${categoryId}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    return null;
  }
}

// Usage
const trends = await getTrends('IN', 3);
console.log(trends);
```

### Axios
```javascript
const axios = require('axios');

axios.get('http://localhost:8000/trends/IN/3')
  .then(response => {
    const data = response.data;
    console.log(`Category: ${data.category}`);
    console.log(`Cached: ${data.cached}`);
  })
  .catch(error => console.error('Error:', error));
```

## Integration Examples

### Save to Database (Python + SQLite)
```python
import requests
import sqlite3

# Fetch data
response = requests.get("http://localhost:8000/trends/IN/3")
data = response.json()

# Save to database
conn = sqlite3.connect('trends.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS trends (
        id INTEGER PRIMARY KEY,
        category TEXT,
        trend TEXT,
        search_volume TEXT,
        started TEXT,
        timestamp TEXT
    )
''')

for trend in data['data']:
    cursor.execute('''
        INSERT INTO trends (category, trend, search_volume, started, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['category'],
        trend['trends'],
        trend['search_volume'],
        trend['started'],
        data['timestamp']
    ))

conn.commit()
conn.close()
```

### Build a Dashboard (Streamlit)
```python
import streamlit as st
import requests
import pandas as pd

st.title("Google Trends Dashboard")

geo = st.selectbox("Select Geography", ["IN", "US", "GB", "CA"])
category_id = st.selectbox("Select Category", [
    (3, "Business and finance"),
    (18, "Technology"),
    (17, "Sports")
])

if st.button("Fetch Trends"):
    with st.spinner("Fetching data..."):
        response = requests.get(f"http://localhost:8000/trends/{geo}/{category_id[0]}")
        data = response.json()
        
        st.success(f"Found {len(data['data'])} trends")
        
        df = pd.DataFrame(data['data'])
        st.dataframe(df)
        
        st.metric("Category", data['category'])
        st.metric("Cached", data['cached'])
```

### Scheduled Data Collection (Python + APScheduler)
```python
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import json
from datetime import datetime

def fetch_and_save_trends():
    """Fetch trends every hour and save to file"""
    response = requests.get("http://localhost:8000/trends/IN?max_workers=5")
    data = response.json()
    
    filename = f"trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved {data['successful']} categories to {filename}")

scheduler = BlockingScheduler()
scheduler.add_job(fetch_and_save_trends, 'interval', hours=1)
scheduler.start()
```

## Real-World Use Cases

### 1. News Website - Trending Topics Widget
```python
# Fetch top 5 trends from multiple categories
categories = [3, 4, 17]  # Business, Entertainment, Sports
all_trends = []

for cat_id in categories:
    response = requests.get(f"http://localhost:8000/trends/IN/{cat_id}")
    data = response.json()
    all_trends.extend(data['data'][:5])

# Display in widget
for trend in all_trends[:10]:
    print(f"🔥 {trend['trends']} ({trend['search_volume']})")
```

### 2. Market Research - Track Brand Mentions
```python
# Monitor if your brand appears in trends
brand_name = "YourBrand"

response = requests.get("http://localhost:8000/trends/IN")
data = response.json()

for category in data['categories']:
    for trend in category['data']:
        if brand_name.lower() in trend['trends'].lower():
            print(f"🎯 Found in {category['category']}: {trend['trends']}")
```

### 3. Content Creation - Topic Ideas
```python
# Get trending topics for blog post ideas
response = requests.get("http://localhost:8000/trends/IN/18")  # Technology
data = response.json()

print("📝 Blog Post Ideas:")
for i, trend in enumerate(data['data'][:5], 1):
    print(f"{i}. {trend['trends']}")
    print(f"   Volume: {trend['search_volume']}")
    print(f"   Link: {trend['explore_link']}\n")
```

## Testing & Monitoring

### Load Testing (with locust)
```python
from locust import HttpUser, task

class TrendsUser(HttpUser):
    @task
    def get_categories(self):
        self.client.get("/categories")
    
    @task(3)
    def get_single_category(self):
        self.client.get("/trends/IN/3")
```

### Health Check Monitoring
```bash
# Add to crontab for monitoring
*/5 * * * * curl -f http://localhost:8000/health || echo "API Down!" | mail -s "Alert" admin@example.com
```
