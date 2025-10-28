# Google Trends API - Open Source

🚀 **Real-time REST API for Google Trends data with JSON responses**

Transform Google Trends data into structured JSON via simple HTTP requests. Perfect for building dashboards, analytics tools, or integrating trends data into your applications.

## ✨ Features

- 🌐 **REST API** - Simple HTTP endpoints returning JSON
- ⚡ **Real-time scraping** - Fresh data on every request
- 💾 **Smart caching** - 1-hour TTL to reduce load
- 🔄 **Parallel processing** - Fast responses with concurrent scraping
- 📊 **All 20 categories** - Complete Google Trends category coverage
- 🌍 **Any geography** - Support for all country codes (IN, US, GB, etc.)
- 📖 **Auto documentation** - Interactive Swagger UI at `/docs`
- 🔓 **Open source** - MIT licensed, free to use and modify

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/sairam030/Google-Trends-CSV-Downloader.git
cd Google-Trends-CSV-Downloader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-api.txt
```

### Run the API

```bash
# Development mode with auto-reload
python api.py

# Or using uvicorn directly
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📡 API Endpoints

### 1️⃣ Get All Categories List

```bash
GET /categories
```

**Response:**
```json
{
  "total": 20,
  "categories": [
    {"name": "All Categories", "id": 0},
    {"name": "Business and finance", "id": 3},
    {"name": "Technology", "id": 18}
  ]
}
```

### 2️⃣ Get Single Category Trends

```bash
GET /trends/{geo}/{category_id}
```

**Example:**
```bash
curl http://localhost:8000/trends/IN/3
```

**Response:**
```json
{
  "category": "Business and finance",
  "category_id": 3,
  "geo": "IN",
  "data": [
    {
      "trends": "gold rate today",
      "search_volume": "500K+",
      "started": "October 28 2025 at 12:00 AM",
      "ended": "October 28 2025 at 11:59 PM",
      "trend_breakdown": "Breakout",
      "explore_link": "https://trends.google.com/..."
    }
  ],
  "timestamp": "2025-10-28T10:30:00",
  "cached": false
}
```

### 3️⃣ Get ALL Categories (Parallel)

```bash
GET /trends/{geo}?max_workers=3
```

**Example:**
```bash
curl http://localhost:8000/trends/IN?max_workers=5
```

**Response:**
```json
{
  "geo": "IN",
  "total_categories": 20,
  "successful": 18,
  "failed": 1,
  "empty": 1,
  "categories": [
    {
      "category": "Business and finance",
      "category_id": 3,
      "geo": "IN",
      "data": [...],
      "timestamp": "2025-10-28T10:30:00",
      "cached": false
    }
  ],
  "timestamp": "2025-10-28T10:30:00",
  "execution_time": 45.2
}
```

### 4️⃣ Health Check

```bash
GET /health
```

### 5️⃣ Clear Cache

```bash
DELETE /cache
```

## 🌍 Supported Geographies

Use any valid country code:
- `IN` - India
- `US` - United States
- `GB` - United Kingdom
- `CA` - Canada
- `AU` - Australia
- `DE` - Germany
- `FR` - France
- `JP` - Japan
- And many more...

## 📊 Available Categories

| Category | ID | Category | ID |
|----------|-------|----------|-------|
| All Categories | 0 | Law and government | 10 |
| Autos and vehicles | 1 | Other | 11 |
| Beauty and fashion | 2 | Pets and animals | 13 |
| Business and finance | 3 | Politics | 14 |
| Climate | 20 | Science | 15 |
| Entertainment | 4 | Shopping | 16 |
| Food and drink | 5 | Sports | 17 |
| Games | 6 | Technology | 18 |
| Health | 7 | Travel and transportation | 19 |
| Hobbies and leisure | 8 | Jobs and education | 9 |

## 💡 Usage Examples

### Python
```python
import requests

# Get all trends for India
response = requests.get("http://localhost:8000/trends/IN")
data = response.json()

print(f"Found {data['successful']} categories")
for category in data['categories']:
    print(f"{category['category']}: {len(category['data'])} trends")
```

### JavaScript/Node.js
```javascript
fetch('http://localhost:8000/trends/IN/3')
  .then(res => res.json())
  .then(data => {
    console.log(`Category: ${data.category}`);
    data.data.forEach(trend => {
      console.log(`- ${trend.trends}: ${trend.search_volume}`);
    });
  });
```

### cURL
```bash
# Get business trends for India
curl http://localhost:8000/trends/IN/3 | jq '.data[] | .trends'

# Get all categories for US with 5 workers
curl "http://localhost:8000/trends/US?max_workers=5" | jq '.successful'
```

## ⚡ Performance

- **Single category**: ~3-5 seconds
- **All categories (sequential)**: ~60-90 seconds
- **All categories (parallel, 5 workers)**: ~15-25 seconds
- **Cached responses**: <100ms

## 🔧 Configuration

Edit `api.py` to customize:

```python
# Cache duration (default: 1 hour)
CACHE_TTL = 3600

# Max parallel workers (default: 5)
max_workers = min(max_workers, 5)

# API host and port
uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🐳 Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Chrome dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY api.py .

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t google-trends-api .
docker run -p 8000:8000 google-trends-api
```

## ☁️ Cloud Deployment

### Deploy to Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Deploy to Render
1. Connect your GitHub repo to Render
2. Create a new Web Service
3. Build command: `pip install -r requirements-api.txt`
4. Start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

### Deploy to Heroku
```bash
# Create Procfile
echo "web: uvicorn api:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create google-trends-api
git push heroku main
```

## 🔒 Security Best Practices

For production deployment:

1. **Add rate limiting:**
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.get("/trends/{geo}")
@limiter.limit("10/minute")
async def get_all_categories(request: Request, geo: str):
    ...
```

2. **Add authentication:**
```python
from fastapi.security import HTTPBearer
security = HTTPBearer()

@app.get("/trends/{geo}")
async def get_all_categories(geo: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Validate API key
    ...
```

3. **Update CORS settings:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use this in your projects!

## 🙏 Acknowledgments

- Google Trends for providing the data
- FastAPI for the excellent framework
- Selenium for web automation

## 📧 Contact

Created by [@sairam030](https://github.com/sairam030)

---

**⭐ If you find this useful, please star the repo!**
