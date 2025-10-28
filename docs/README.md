# 🚀 Google Trends API - Production Ready

**Real-time Google Trends data via clean REST API**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [Examples](#-examples)
- [Production Deployment](#-production-deployment)
- [Configuration](#-configuration)
- [Development](#-development)

---

## ✨ Features

- **🌐 RESTful API** - Clean, intuitive endpoints
- **⚡ Real-time scraping** - Fresh data on every request
- **💾 Smart caching** - 1-hour TTL for performance
- **🔄 Parallel processing** - Fast responses with concurrent scraping
- **📊 20 Categories** - Complete Google Trends coverage
- **🌍 Global support** - Any country code (IN, US, GB, etc.)
- **📖 Auto docs** - Interactive Swagger UI at `/docs`
- **🐳 Docker ready** - Easy deployment with Docker Compose
- **🔒 Production-grade** - Logging, error handling, health checks
- **📈 Monitoring** - Health endpoint for uptime monitoring

---

## 🚀 Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/sairam030/Google-Trends-CSV-Downloader.git
cd Google-Trends-CSV-Downloader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the API
python src/main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### Docker (Recommended for Production)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 📡 API Endpoints

### Base URL
```
http://localhost:8000
```

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/{geo}` | Get all trends for a geography |
| GET | `/api/v1/{geo}/{category}` | Get trends for specific category |
| GET | `/categories` | List all available categories |
| GET | `/health` | Health check |
| GET | `/docs` | Interactive API documentation |

---

### 1️⃣ Get All Trends

Get ALL trends from ALL categories as a flat list.

**Endpoint:**
```
GET /api/v1/{geo}?workers=3
```

**Parameters:**
- `geo` (required): Country code (IN, US, GB, CA, etc.)
- `workers` (optional): Parallel workers (1-5, default: 3)

**Example:**
```bash
curl "http://localhost:8000/api/v1/IN?workers=5"
```

**Response:**
```json
{
  "geo": "IN",
  "total_categories": 20,
  "successful_categories": 18,
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
  "execution_time": 45.2,
  "cached": false
}
```

---

### 2️⃣ Get Category Trends

Get trends for a specific category only.

**Endpoint:**
```
GET /api/v1/{geo}/{category}
```

**Parameters:**
- `geo` (required): Country code
- `category` (required): Category slug (see `/categories`)

**Available Categories:**
```
all, autos, beauty, business, entertainment, food, games, health,
hobbies, education, law, other, pets, politics, science, shopping,
sports, technology, travel, climate
```

**Examples:**
```bash
# Technology trends in USA
curl "http://localhost:8000/api/v1/US/technology"

# Sports trends in UK
curl "http://localhost:8000/api/v1/GB/sports"

# Business trends in India
curl "http://localhost:8000/api/v1/IN/business"
```

**Response:**
```json
{
  "geo": "IN",
  "category": "Technology",
  "category_id": 18,
  "category_slug": "technology",
  "total_trends": 15,
  "trends": [
    {
      "trends": "gmail passwords exposed",
      "search_volume": "5K+",
      "started": "...",
      "ended": "",
      "trend_breakdown": "...",
      "explore_link": "..."
    }
  ],
  "timestamp": "2025-10-28T21:20:00",
  "cached": false
}
```

---

### 3️⃣ List Categories

Get all available categories with their slugs and IDs.

**Endpoint:**
```
GET /categories
```

**Example:**
```bash
curl "http://localhost:8000/categories"
```

**Response:**
```json
{
  "total": 20,
  "categories": [
    {
      "slug": "business",
      "id": 3,
      "name": "Business and finance"
    },
    {
      "slug": "technology",
      "id": 18,
      "name": "Technology"
    }
  ]
}
```

---

### 4️⃣ Health Check

Monitor API health and uptime.

**Endpoint:**
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-28T21:25:00",
  "cache_size": 5,
  "uptime": "operational"
}
```

---

## 💡 Examples

### Python

```python
import requests

# Get all trends for India
response = requests.get("http://localhost:8000/api/v1/IN?workers=5")
data = response.json()

print(f"Found {data['total_trends']} trends")

# Filter by category
tech_trends = [t for t in data['trends'] if t['category'] == 'Technology']
print(f"Technology trends: {len(tech_trends)}")

# Get specific category
tech = requests.get("http://localhost:8000/api/v1/IN/technology").json()
print(f"Technology: {tech['total_trends']} trends")
```

### JavaScript

```javascript
// Fetch all trends
fetch('http://localhost:8000/api/v1/IN?workers=5')
  .then(res => res.json())
  .then(data => {
    console.log(`Total trends: ${data.total_trends}`);
    data.trends.forEach(trend => {
      console.log(`[${trend.category}] ${trend.trends}: ${trend.search_volume}`);
    });
  });

// Fetch specific category
fetch('http://localhost:8000/api/v1/US/technology')
  .then(res => res.json())
  .then(data => {
    console.log(`Technology trends: ${data.total_trends}`);
  });
```

### cURL

```bash
# Get all trends for India
curl "http://localhost:8000/api/v1/IN?workers=5" | jq '.total_trends'

# Get sports trends for USA
curl "http://localhost:8000/api/v1/US/sports" | jq '.trends[] | .trends'

# Pretty print
curl -s "http://localhost:8000/api/v1/IN/technology" | python3 -m json.tool
```

---

## 🚢 Production Deployment

### Docker Deployment (Recommended)

```bash
# Build image
docker build -t google-trends-api .

# Run container
docker run -d \
  -p 8000:8000 \
  --name trends-api \
  --restart unless-stopped \
  google-trends-api

# View logs
docker logs -f trends-api
```

### Docker Compose

```bash
# Start
docker-compose up -d

# Scale (multiple instances)
docker-compose up -d --scale api=3

# Stop
docker-compose down
```

### Cloud Platforms

#### Railway
```bash
railway login
railway init
railway up
```

#### Render
1. Connect GitHub repo
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

#### Heroku
```bash
# Create Procfile
echo "web: uvicorn src.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create google-trends-api
git push heroku main
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file:

```bash
# Server
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# Cache
CACHE_TTL=3600

# Scraping
MAX_WORKERS=5
DOWNLOAD_TIMEOUT=40

# CORS
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `LOG_LEVEL` | info | Logging level |
| `CACHE_TTL` | 3600 | Cache duration (seconds) |
| `MAX_WORKERS` | 5 | Max parallel workers |
| `CORS_ORIGINS` | * | Allowed CORS origins |

---

## 🔧 Development

### Project Structure

```
Google-Trends-CSV-Downloader/
├── src/
│   └── main.py              # Main API application
├── config/
│   └── settings.py          # Configuration settings
├── docs/
│   └── API.md              # API documentation
├── tests/
│   └── test_api.py         # API tests
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image
├── docker-compose.yml      # Docker Compose config
├── .env.example            # Environment template
└── README.md               # This file
```

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov httpx

# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

### Code Quality

```bash
# Format code
pip install black
black src/

# Lint
pip install pylint
pylint src/

# Type checking
pip install mypy
mypy src/
```

---

## 📊 Performance

| Operation | Cold (First Request) | Warm (Cached) |
|-----------|---------------------|---------------|
| Single category | ~3-5 seconds | <100ms |
| All categories (3 workers) | ~20-30 seconds | <100ms |
| All categories (5 workers) | ~15-25 seconds | <100ms |

**Optimization Tips:**
- Use more workers for faster responses (max 5)
- Enable caching for frequent requests
- Deploy close to your users geographically
- Use CDN for static content

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Google Trends for providing the data
- FastAPI for the excellent framework
- Selenium for web automation

---

## 📧 Contact

**Author**: [@sairam030](https://github.com/sairam030)

**Repository**: [Google-Trends-CSV-Downloader](https://github.com/sairam030/Google-Trends-CSV-Downloader)

---

**⭐ If you find this useful, please star the repo!**
