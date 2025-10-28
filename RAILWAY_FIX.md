# Railway ChromeDriver Fix

## Problem
Railway deployment was failing with error:
```
[Errno 8] Exec format error: '/root/.wdm/drivers/chromedriver/linux64/141.0.7390.122/chromedriver-linux64/THIRD_PARTY_NOTICES.chromedriver'
```

**Root Cause**: WebDriver Manager was caching the wrong file (text file instead of executable) and trying to execute it.

## Solution

### Changes Made

1. **Dockerfile** - Added environment variable to disable WebDriver Manager:
   ```dockerfile
   ENV WDM_LOCAL=1
   ```

2. **start.sh** - Enhanced startup script with:
   - ChromeDriver verification
   - Path detection (supports both `/usr/bin/chromedriver` and `/usr/bin/chromium-driver`)
   - Detailed logging for debugging
   - Automatic fallback paths

3. **src/main.py** - Improved ChromeDriver initialization:
   - Reads from `CHROMEDRIVER_PATH` environment variable
   - Tries multiple paths as fallback
   - Logs the actual path being used
   - Added ChromeDriver health check to `/health` endpoint

4. **Health Check** - `/health` endpoint now reports:
   - ChromeDriver availability
   - ChromeDriver path
   - Status: "healthy" or "degraded"

## Deployment Steps

### Railway Deployment

1. **Push Changes**:
   ```bash
   git add .
   git commit -m "Fix ChromeDriver exec format error in Railway"
   git push
   ```

2. **Verify Deployment**:
   - Check Railway logs for ChromeDriver verification messages
   - Look for: "ChromeDriver: ChromeDriver X.X.X"
   - Verify no more "Exec format error" messages

3. **Test Health Endpoint**:
   ```bash
   curl https://your-app.railway.app/health
   ```
   
   Should return:
   ```json
   {
     "status": "healthy",
     "chromedriver": {
       "available": true,
       "path": "/usr/bin/chromedriver"
     }
   }
   ```

4. **Test API**:
   ```bash
   curl https://your-app.railway.app/api/v1/IN/sports
   ```

### Local Development

No changes needed - script auto-detects environment:
```bash
./start.sh
```

## Verification Checklist

- [ ] No "Exec format error" in Railway logs
- [ ] `/health` shows ChromeDriver available
- [ ] API endpoints return data (not 404)
- [ ] Logs show "Successfully scraped X trends"
- [ ] No WDM (WebDriver Manager) errors

## Troubleshooting

### If ChromeDriver still not found:

1. Check Railway logs for:
   ```
   🔍 Verifying ChromeDriver...
   ChromeDriver: [version]
   Path: /usr/bin/chromedriver
   ```

2. SSH into Railway container:
   ```bash
   railway run bash
   which chromedriver
   ls -la /usr/bin/chrome*
   ```

3. Verify Dockerfile installed chromium-driver:
   ```bash
   dpkg -l | grep chromium
   ```

### If WDM still appears in logs:

This shouldn't happen anymore, but if it does:
- Ensure `WDM_LOCAL=1` is set in Dockerfile
- Clear Railway build cache and redeploy

## Architecture Notes

**Before**: Used webdriver-manager which auto-downloads ChromeDriver
- ❌ Downloaded wrong file in Railway environment
- ❌ Cache corruption issues
- ❌ Unpredictable behavior

**After**: Uses system ChromeDriver from Dockerfile
- ✅ Installed via `apt-get install chromium-driver`
- ✅ Predictable location (`/usr/bin/chromedriver`)
- ✅ No auto-download or caching issues
- ✅ Same ChromeDriver version every deployment

## Performance Impact

**None** - Actually faster because:
- No ChromeDriver download on startup
- No cache checks
- ChromeDriver pre-installed in image

## Related Files

- `Dockerfile` - ChromeDriver installation and env vars
- `start.sh` - Startup verification script
- `src/main.py` - ChromeDriver service initialization
- `requirements.txt` - No webdriver-manager dependency
