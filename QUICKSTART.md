# 🚀 Google Trends API - Quick Reference

## Production-Ready Endpoints

### Base URL
```
http://localhost:8000
```

## 📡 Main Endpoints

### 1. Get All Trends (All Categories)
```bash
GET /api/v1/{geo}?workers=5

# Examples
curl "http://localhost:8000/api/v1/IN?workers=5"
curl "http://localhost:8000/api/v1/US?workers=3"
curl "http://localhost:8000/api/v1/GB"
```

**Returns:** Flat array with ALL trends, each having `category` field

---

### 2. Get Category Trends
```bash
GET /api/v1/{geo}/{category}

# Examples
curl "http://localhost:8000/api/v1/IN/technology"
curl "http://localhost:8000/api/v1/US/sports"
curl "http://localhost:8000/api/v1/GB/business"
```

**Returns:** Trends for specific category only

---

### 3. List Categories
```bash
GET /categories

curl "http://localhost:8000/categories"
```

---

## 🏷️ Category Slugs

| Slug | Name |
|------|------|
| `all` | All Categories |
| `autos` | Autos and vehicles |
| `beauty` | Beauty and fashion |
| `business` | Business and finance |
| `entertainment` | Entertainment |
| `food` | Food and drink |
| `games` | Games |
| `health` | Health |
| `hobbies` | Hobbies and leisure |
| `education` | Jobs and education |
| `law` | Law and government |
| `other` | Other |
| `pets` | Pets and animals |
| `politics` | Politics |
| `science` | Science |
| `shopping` | Shopping |
| `sports` | Sports |
| `technology` | Technology |
| `travel` | Travel and transportation |
| `climate` | Climate |

---

## 🌍 Geography Codes

`IN` (India), `US` (USA), `GB` (UK), `CA` (Canada), `AU` (Australia), `DE` (Germany), `FR` (France), `JP` (Japan), etc.

---

## 🚦 Quick Commands

### Start API
```bash
./start.sh                    # Recommended
python src/main.py            # Manual
docker-compose up -d          # Docker
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Get all trends
curl "http://localhost:8000/api/v1/IN?workers=5"

# Get specific category
curl "http://localhost:8000/api/v1/IN/technology"

# List categories
curl "http://localhost:8000/categories"
```

### Stop API
```bash
pkill -f "python src/main.py"  # Manual
docker-compose down            # Docker
```

---

## 📊 Response Format

### All Trends
```json
{
  "geo": "IN",
  "total_trends": 450,
  "trends": [
    {
      "category": "Technology",
      "category_id": 18,
      "trends": "gmail passwords exposed",
      "search_volume": "5K+",
      "started": "...",
      "ended": "",
      "trend_breakdown": "...",
      "explore_link": "..."
    }
  ]
}
```

### Single Category
```json
{
  "geo": "IN",
  "category": "Technology",
  "category_slug": "technology",
  "total_trends": 5,
  "trends": [...]
}
```

---

## 🔧 Configuration

Edit `.env` file:
```bash
HOST=0.0.0.0
PORT=8000
CACHE_TTL=3600
MAX_WORKERS=5
LOG_LEVEL=info
```

---

## 📖 Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Full README**: See [README.md](README.md)

---

## 🎯 Production Checklist

- ✅ Clean RESTful endpoints
- ✅ API versioning (/api/v1/)
- ✅ Human-readable category slugs
- ✅ Proper error handling
- ✅ Structured logging
- ✅ Health monitoring
- ✅ Docker support
- ✅ Environment config
- ✅ Caching (1-hour TTL)
- ✅ CORS enabled
- ✅ Comprehensive docs

---

**Your API is production-ready! 🎉**
