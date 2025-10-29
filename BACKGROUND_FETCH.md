# Background Data Fetching - Version 2.0

## 🚀 New Features

### Instant API Responses
- API calls return data **instantly** from cache
- No more waiting 30-60 seconds for scraping
- Response time: **<100ms** instead of 30-60 seconds

### Auto-Refresh Mechanism
- Background task fetches fresh data every **30 minutes**
- Runs automatically in the background
- Doesn't block API requests

### Persistent Storage
- Data saved to disk in `cache_data/` directory
- Survives server restarts
- Pre-loaded on startup

### Multi-Geography Support
- Auto-fetches data for: **IN, US, GB, AU, CA**
- Easily configurable via environment variables
- Add more countries as needed

## 📊 How It Works

```
┌─────────────┐
│   Startup   │
└──────┬──────┘
       │
       ├─> Load cached data from disk
       │
       ├─> Start background scheduler
       │
       └─> Fetch immediately if no cache
       
┌──────────────────┐
│ Every 30 minutes │
└────────┬─────────┘
         │
         ├─> Scrape all categories for each GEO
         │
         ├─> Save to memory cache
         │
         └─> Save to disk (persistent)

┌───────────────┐
│  API Request  │
└───────┬───────┘
        │
        ├─> Check memory cache (instant!)
        │
        ├─> Check disk cache (if not in memory)
        │
        └─> Fetch live (only if no cache)
```

## 🔧 Configuration

### Environment Variables

```bash
# Refresh interval (in minutes)
REFRESH_INTERVAL_MINUTES=30

# Geographies to auto-fetch (comma-separated)
DEFAULT_GEOS=IN,US,GB,AU,CA,FR,DE,JP

# Number of parallel workers
MAX_WORKERS=3

# Cache directory
CACHE_DIR=cache_data
```

### Example `.env` File

```env
REFRESH_INTERVAL_MINUTES=15
DEFAULT_GEOS=IN,US
MAX_WORKERS=5
```

## 📡 New API Endpoints

### 1. Check Background Fetch Status
```http
GET /status
```

**Response:**
```json
{
  "refresh_interval_minutes": 30,
  "supported_geos": ["IN", "US", "GB", "AU", "CA"],
  "fetch_status": {
    "status": "completed",
    "last_fetch": "2025-10-29T10:30:00",
    "next_fetch": "2025-10-29T11:00:00",
    "fetched_geos": [
      {"geo": "IN", "timestamp": "...", "status": "success"},
      {"geo": "US", "timestamp": "...", "status": "success"}
    ]
  },
  "cache": {
    "in_memory_count": 5,
    "disk_files": 5
  }
}
```

### 2. Manual Refresh
```http
POST /refresh/{geo}
```

**Example:**
```bash
curl -X POST https://your-api.railway.app/refresh/IN
```

**Response:**
```json
{
  "message": "Refresh started for IN",
  "status": "processing",
  "note": "Data will be updated in background. Check /status for progress."
}
```

### 3. Enhanced Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-29T10:45:00",
  "cache_size": 5,
  "background_fetch": {
    "status": "scheduled",
    "last_fetch": "2025-10-29T10:30:00",
    "next_fetch": "2025-10-29T11:00:00"
  },
  "chromedriver": {
    "available": true,
    "path": "/usr/bin/chromedriver"
  }
}
```

## 🎯 Usage Examples

### Get All Trends (Instant!)
```bash
# Before: 30-60 seconds
# After: <100ms

curl https://your-api.railway.app/api/v1/IN
```

### Get Category Trends (Filtered from Cache)
```bash
# Filters from cached data - super fast!
curl https://your-api.railway.app/api/v1/IN/sports
```

### Check What's Cached
```bash
curl https://your-api.railway.app/status
```

### Force Refresh
```bash
curl -X POST https://your-api.railway.app/refresh/US
```

## 📁 File Structure

```
cache_data/
├── IN_all.json       # All trends for India
├── US_all.json       # All trends for USA
├── GB_all.json       # All trends for UK
├── AU_all.json       # All trends for Australia
└── CA_all.json       # All trends for Canada
```

Each file contains:
- All categories
- All trends
- Metadata (timestamp, execution time, etc.)
- Ready to serve instantly

## 🔍 Monitoring

### Check Logs

```bash
# Railway
railway logs

# Local
docker-compose logs -f
```

### Log Messages to Look For

```
🚀 Starting Google Trends API v2.0.0
📂 Loading cached data from disk...
  Loaded: IN_all.json
  Loaded: US_all.json
✅ Loaded 5 cached datasets from disk
✅ Background scheduler started (refresh every 30 minutes)
🔄 Background fetch started for IN
✅ Background fetch completed for IN: 150 trends in 25.3s
```

## ⚡ Performance Comparison

### Before (v1.0)
```
Request: /api/v1/IN
Response Time: 30-60 seconds ❌
Server Load: High (scraping on every request)
User Experience: Poor (long wait times)
```

### After (v2.0)
```
Request: /api/v1/IN
Response Time: <100ms ✅
Server Load: Low (pre-fetched data)
User Experience: Excellent (instant responses)
```

## 🛠️ Troubleshooting

### No Data on First Request?
```bash
# Check if background fetch is running
curl https://your-api.railway.app/status

# Manually trigger refresh
curl -X POST https://your-api.railway.app/refresh/IN
```

### Want to Change Refresh Interval?
```bash
# In Railway dashboard, add environment variable:
REFRESH_INTERVAL_MINUTES=15  # Refresh every 15 minutes
```

### Want to Add More Countries?
```bash
# In Railway dashboard:
DEFAULT_GEOS=IN,US,GB,AU,CA,FR,DE,JP,BR,MX
```

### Cache Not Persisting?
```bash
# Check if cache_data directory exists
ls -la cache_data/

# Check permissions
chmod 755 cache_data
```

## 📈 Scaling

### For More Traffic
- Increase `DEFAULT_GEOS` to pre-fetch more countries
- Decrease `REFRESH_INTERVAL_MINUTES` for fresher data
- Increase Railway resources if needed

### For Less Resources
- Reduce `DEFAULT_GEOS` to only essential countries
- Increase `REFRESH_INTERVAL_MINUTES` to reduce scraping
- Set `MAX_WORKERS=1` to reduce parallel load

## 🔐 Production Recommendations

1. **Set appropriate refresh interval**
   ```env
   REFRESH_INTERVAL_MINUTES=30  # Good balance
   ```

2. **Choose your geographies wisely**
   ```env
   DEFAULT_GEOS=IN,US,GB  # Only what you need
   ```

3. **Monitor cache health**
   - Check `/health` endpoint regularly
   - Set up alerts on `/status`

4. **Consider Railway persistence**
   - Cache survives restarts
   - But Railway ephemeral storage resets on redeploy
   - Consider adding volume mount for production

## 🎉 Benefits

✅ **Instant responses** - <100ms vs 30-60 seconds
✅ **Better UX** - No loading spinners needed
✅ **Lower costs** - Less compute time per request
✅ **More reliable** - Cached data available even if scraping fails
✅ **Scalable** - Handle 1000s of requests without issues
✅ **Smart** - Auto-refreshes in background
✅ **Persistent** - Survives server restarts

## 🚀 Deploy to Railway

```bash
# Commit changes
git add .
git commit -m "Add background fetch v2.0"

# Push to Railway
git push

# Check logs
railway logs

# Test status
curl https://your-app.railway.app/status
```

## 📝 Version History

- **v2.0** - Background fetching, instant responses, persistent storage
- **v1.0** - Basic API with on-demand scraping
