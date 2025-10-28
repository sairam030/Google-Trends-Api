# 🌟 Flat List API - The Simplest Way to Get Google Trends

## What's New?

**New Endpoint**: `GET /trends/{geo}` - Returns ALL trends from ALL categories as a single flat array, with each trend having a `category` field!

---

## 🎯 The Problem It Solves

**Before**: You had to loop through categories or parse nested JSON:
```json
{
  "categories": [
    {
      "category": "Business",
      "data": [...]
    },
    {
      "category": "Technology",
      "data": [...]
    }
  ]
}
```

**Now**: Single flat array with category in each trend:
```json
{
  "trends": [
    {
      "category": "Business and finance",
      "category_id": 3,
      "trends": "amazon layoffs",
      "search_volume": "50K+",
      "started": "...",
      "ended": "",
      "trend_breakdown": "...",
      "explore_link": "..."
    },
    {
      "category": "Technology",
      "category_id": 18,
      "trends": "gmail passwords exposed",
      "search_volume": "5K+",
      ...
    }
  ]
}
```

---

## 🚀 Quick Start

### Basic Request
```bash
curl "http://localhost:8000/trends/IN"
```

### With More Workers (Faster)
```bash
curl "http://localhost:8000/trends/IN?max_workers=5"
```

---

## 📊 Response Format

```json
{
  "geo": "IN",
  "total_categories": 20,
  "successful_categories": 18,
  "failed_categories": 1,
  "empty_categories": 1,
  "total_trends": 450,
  "trends": [
    {
      "category": "Business and finance",
      "category_id": 3,
      "trends": "amazon layoffs",
      "search_volume": "50K+",
      "started": "October 28, 2025 at 3:00:00 AM UTC+5:30",
      "ended": "",
      "trend_breakdown": "amazon layoffs,amazon layoffs employees",
      "explore_link": "https://trends.google.com/trends/explore?..."
    }
  ],
  "timestamp": "2025-10-28T21:15:00",
  "execution_time": 48.83,
  "cached": false
}
```

---

## 🎨 Usage Examples

### 1. Get All Trends for India
```bash
curl "http://localhost:8000/trends/IN?max_workers=3"
```

### 2. Python - Display All Trends
```python
import requests

response = requests.get("http://localhost:8000/trends/IN?max_workers=5")
data = response.json()

print(f"Found {data['total_trends']} trends from {data['successful_categories']} categories")

for trend in data['trends']:
    print(f"[{trend['category']}] {trend['trends']}: {trend['search_volume']}")
```

### 3. Python - Filter by Category
```python
import requests

response = requests.get("http://localhost:8000/trends/IN")
data = response.json()

# Get only Technology trends
tech_trends = [t for t in data['trends'] if t['category'] == 'Technology']

print(f"Technology Trends ({len(tech_trends)}):")
for trend in tech_trends:
    print(f"  • {trend['trends']}: {trend['search_volume']}")
```

### 4. Python - Group by Category
```python
import requests
from collections import defaultdict

response = requests.get("http://localhost:8000/trends/IN")
data = response.json()

# Group trends by category
by_category = defaultdict(list)
for trend in data['trends']:
    by_category[trend['category']].append(trend)

# Display
for category, trends in by_category.items():
    print(f"\n{category}: {len(trends)} trends")
    for trend in trends[:5]:  # First 5
        print(f"  • {trend['trends']} ({trend['search_volume']})")
```

### 5. Python - Save to CSV
```python
import requests
import csv

response = requests.get("http://localhost:8000/trends/IN")
data = response.json()

with open('all_trends.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'category', 'category_id', 'trends', 'search_volume', 
        'started', 'ended', 'trend_breakdown', 'explore_link'
    ])
    writer.writeheader()
    writer.writerows(data['trends'])

print(f"Saved {len(data['trends'])} trends to all_trends.csv")
```

### 6. JavaScript - Fetch and Display
```javascript
fetch('http://localhost:8000/trends/IN?max_workers=5')
  .then(res => res.json())
  .then(data => {
    console.log(`Total Trends: ${data.total_trends}`);
    
    data.trends.forEach(trend => {
      console.log(`[${trend.category}] ${trend.trends}: ${trend.search_volume}`);
    });
  });
```

### 7. JavaScript - Filter and Sort
```javascript
const response = await fetch('http://localhost:8000/trends/IN');
const data = await response.json();

// Get high-volume trends (50K+)
const hotTrends = data.trends.filter(t => t.search_volume === '50K+');

// Sort by category
const sorted = data.trends.sort((a, b) => 
  a.category.localeCompare(b.category)
);

console.log('Hot Trends:', hotTrends);
```

### 8. Search for Specific Keywords
```python
import requests

response = requests.get("http://localhost:8000/trends/IN")
data = response.json()

keyword = "price"
matches = [t for t in data['trends'] if keyword.lower() in t['trends'].lower()]

print(f"Trends containing '{keyword}': {len(matches)}")
for trend in matches[:10]:
    print(f"  [{trend['category']}] {trend['trends']}")
```

---

## 🔄 Comparison: Three API Styles

### Style 1: Single Category (Original)
```bash
GET /trends/IN/3
```
**Use when**: You want data from ONE specific category only

**Response**:
```json
{
  "category": "Business and finance",
  "data": [...]
}
```

---

### Style 2: Grouped by Category
```bash
GET /trends/IN/all
```
**Use when**: You want to process each category separately

**Response**:
```json
{
  "categories": [
    {"category": "Business", "data": [...]},
    {"category": "Tech", "data": [...]}
  ]
}
```

---

### Style 3: Flat List ⭐ (NEW - RECOMMENDED)
```bash
GET /trends/IN
```
**Use when**: You want ALL trends in one simple array

**Response**:
```json
{
  "trends": [
    {"category": "Business", "trends": "...", ...},
    {"category": "Tech", "trends": "...", ...}
  ]
}
```

---

## 💡 Why Use the Flat List API?

✅ **Simpler**: No nested loops, just one array  
✅ **Flexible**: Easy to filter, search, sort by category  
✅ **CSV-ready**: Matches your original CSV structure  
✅ **Dashboard-friendly**: Perfect for displaying all trends  
✅ **Search-friendly**: Easy to search across all categories  
✅ **Database-ready**: Easy to insert into SQL/NoSQL  

---

## ⚡ Performance

- **Cold (first request)**: ~15-50 seconds (depends on workers)
- **Warm (cached)**: <100ms
- **Cache duration**: 1 hour
- **Recommended workers**: 3-5

---

## 🎯 Real-World Use Cases

### 1. News Dashboard
Show all trending topics regardless of category:
```python
trends = requests.get("http://localhost:8000/trends/IN").json()['trends']
for trend in trends[:20]:  # Top 20
    display_card(trend['trends'], trend['category'], trend['search_volume'])
```

### 2. Search All Trends
Let users search across all categories:
```python
def search_trends(keyword, geo='IN'):
    data = requests.get(f"http://localhost:8000/trends/{geo}").json()
    return [t for t in data['trends'] if keyword.lower() in t['trends'].lower()]

results = search_trends("election")
```

### 3. Category Filter Widget
```javascript
// Load all trends once
const allTrends = await fetch('/trends/IN').then(r => r.json());

// Filter by user selection
function filterByCategory(category) {
  return allTrends.trends.filter(t => t.category === category);
}
```

### 4. Export to Excel
```python
import pandas as pd

data = requests.get("http://localhost:8000/trends/IN").json()
df = pd.DataFrame(data['trends'])
df.to_excel('google_trends.xlsx', index=False)
```

---

## 🔧 Advanced: Custom Filtering

```python
import requests

def get_trends(geo='IN', categories=None, min_volume=None):
    """
    Get trends with optional filtering
    
    Args:
        geo: Country code
        categories: List of category names to include (None = all)
        min_volume: Minimum search volume (e.g., '5K+', '50K+')
    """
    response = requests.get(f"http://localhost:8000/trends/{geo}")
    all_trends = response.json()['trends']
    
    # Filter by category
    if categories:
        all_trends = [t for t in all_trends if t['category'] in categories]
    
    # Filter by volume
    if min_volume:
        volume_order = ['200+', '500+', '1K+', '2K+', '5K+', '10K+', '20K+', '50K+']
        min_idx = volume_order.index(min_volume)
        all_trends = [t for t in all_trends 
                      if t['search_volume'] in volume_order[min_idx:]]
    
    return all_trends

# Usage
hot_tech_trends = get_trends(
    geo='IN',
    categories=['Technology', 'Science'],
    min_volume='5K+'
)
```

---

## 📝 Summary

**Endpoint**: `GET /trends/{geo}?max_workers=3`

**Returns**: Single flat array with all trends, each having:
- `category` - Category name
- `category_id` - Category ID
- `trends` - Trend title
- `search_volume` - Volume (e.g., "50K+")
- `started` - Start time
- `ended` - End time (if applicable)
- `trend_breakdown` - Related keywords
- `explore_link` - Google Trends link

**Perfect for**: Dashboards, search, CSV export, data analysis, any case where you want all trends together!
