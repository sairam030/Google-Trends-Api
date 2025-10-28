"""
Google Trends API - Production Ready
Version: 1.0.0
Clean RESTful endpoints with proper error handling and logging
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import os
import time
import csv
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Google Trends API",
    description="Production-ready API for real-time Google Trends data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# In-memory cache
cache = {}
cache_lock = threading.Lock()
CACHE_TTL = 3600  # 1 hour

# Categories mapping
CATEGORIES = {
    "all": 0,
    "autos": 1,
    "beauty": 2,
    "business": 3,
    "entertainment": 4,
    "food": 5,
    "games": 6,
    "health": 7,
    "hobbies": 8,
    "education": 9,
    "law": 10,
    "other": 11,
    "pets": 13,
    "politics": 14,
    "science": 15,
    "shopping": 16,
    "sports": 17,
    "technology": 18,
    "travel": 19,
    "climate": 20
}

CATEGORY_NAMES = {
    0: "All Categories",
    1: "Autos and vehicles",
    2: "Beauty and fashion",
    3: "Business and finance",
    4: "Entertainment",
    5: "Food and drink",
    6: "Games",
    7: "Health",
    8: "Hobbies and leisure",
    9: "Jobs and education",
    10: "Law and government",
    11: "Other",
    13: "Pets and animals",
    14: "Politics",
    15: "Science",
    16: "Shopping",
    17: "Sports",
    18: "Technology",
    19: "Travel and transportation",
    20: "Climate"
}


def get_cache_key(geo: str, category: Optional[str] = None):
    """Generate cache key"""
    if category:
        return f"{geo}_{category}"
    return f"{geo}_all"


def get_from_cache(cache_key: str):
    """Get data from cache if not expired"""
    with cache_lock:
        if cache_key in cache:
            data, timestamp = cache[cache_key]
            if time.time() - timestamp < CACHE_TTL:
                logger.info(f"Cache HIT: {cache_key}")
                return data
            else:
                del cache[cache_key]
                logger.info(f"Cache EXPIRED: {cache_key}")
    return None


def set_cache(cache_key: str, data):
    """Store data in cache"""
    with cache_lock:
        cache[cache_key] = (data, time.time())
        logger.info(f"Cache SET: {cache_key}")


def scrape_google_trends(url: str, category_name: str, category_id: int, download_dir="temp_downloads") -> Optional[List[Dict]]:
    """
    Scrape Google Trends and return structured data
    """
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-software-rasterizer")
    
    # Set Chrome binary location
    chrome_bin = os.environ.get('CHROME_BIN', '/usr/bin/chromium')
    if os.path.exists(chrome_bin):
        chrome_options.binary_location = chrome_bin

    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    try:
        # Use system ChromeDriver (installed in Docker) instead of webdriver-manager
        # This fixes the "Exec format error" bug in Railway deployment
        chromedriver_path = os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
        
        # Verify chromedriver exists
        if not os.path.exists(chromedriver_path):
            logger.error(f"ChromeDriver not found at {chromedriver_path}")
            # Try alternative path
            chromedriver_path = '/usr/bin/chromium-driver'
            if not os.path.exists(chromedriver_path):
                raise Exception(f"ChromeDriver not found at {chromedriver_path}")
        
        logger.info(f"Using ChromeDriver at: {chromedriver_path}")
        service = ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": os.path.abspath(download_dir)
        })

        existing_files = set(os.listdir(download_dir))
        driver.get(url)
        logger.info(f"Navigated to {url}")

        wait = WebDriverWait(driver, 30)
        time.sleep(5)  # Increased wait for page load
        
        logger.info(f"Page title: {driver.title}")
        
        # Try to find Export button with better error handling
        try:
            export_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Export')]")))
            logger.info("Export button found")
            export_btn.click()
        except Exception as e:
            logger.error(f"Export button not found: {e}")
            # Save page source for debugging
            page_source = driver.page_source
            logger.error(f"Page source length: {len(page_source)}")
            logger.error(f"Page preview: {page_source[:500]}")
            raise

        time.sleep(3)  # Increased wait
        csv_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Download CSV')]")
        logger.info("CSV option found")
        
        if csv_element:
            try:
                parent = csv_element.find_element(By.XPATH, "./ancestor::button | ./ancestor::div[@role='menuitem'] | ./ancestor::*[@role='option']")
                driver.execute_script("arguments[0].click();", parent)
            except:
                driver.execute_script("arguments[0].click();", csv_element)

        download_path = os.path.abspath(download_dir)
        max_wait = 40
        start_time = time.time()
        downloaded_file = None
        
        while time.time() - start_time < max_wait:
            current_files = set(os.listdir(download_path))
            new_files = current_files - existing_files
            csv_files = [f for f in new_files if f.endswith('.csv')]
            
            if csv_files:
                downloaded_file = os.path.join(download_path, csv_files[0])
                time.sleep(1)
                break
            time.sleep(1)
        
        driver.quit()
        
        if not downloaded_file or not os.path.exists(downloaded_file):
            logger.warning(f"No data found for {category_name}")
            return None
        
        # Read CSV and convert to dict
        data = []
        with open(downloaded_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({
                    "trends": row.get("Trends", ""),
                    "search_volume": row.get("Search volume", ""),
                    "started": row.get("Started", ""),
                    "ended": row.get("Ended", ""),
                    "trend_breakdown": row.get("Trend breakdown", ""),
                    "explore_link": row.get("Explore link", "")
                })
        
        # Clean up
        try:
            os.remove(downloaded_file)
        except:
            pass
        
        logger.info(f"Successfully scraped {len(data)} trends from {category_name}")
        return data if data else None
        
    except Exception as e:
        logger.error(f"Error scraping {category_name}: {e}")
        try:
            driver.quit()
        except:
            pass
        return None


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Google Trends API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "GET /api/v1/{geo}": "Get all trends for a geography",
            "GET /api/v1/{geo}/{category}": "Get trends for specific category",
            "GET /categories": "List all available categories",
            "GET /health": "Health check",
            "GET /docs": "API documentation"
        },
        "examples": [
            "/api/v1/IN - All trends for India",
            "/api/v1/US/technology - Technology trends in USA",
            "/api/v1/GB/sports - Sports trends in UK"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_size": len(cache),
        "uptime": "operational"
    }
    
    # Check ChromeDriver availability
    chromedriver_path = os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
    chromedriver_exists = os.path.exists(chromedriver_path)
    
    if not chromedriver_exists:
        # Try alternative path
        chromedriver_path = '/usr/bin/chromium-driver'
        chromedriver_exists = os.path.exists(chromedriver_path)
    
    health_data["chromedriver"] = {
        "available": chromedriver_exists,
        "path": chromedriver_path if chromedriver_exists else "not found"
    }
    
    if not chromedriver_exists:
        health_data["status"] = "degraded"
        health_data["warning"] = "ChromeDriver not found - scraping will fail"
    
    return health_data


@app.get("/categories")
async def list_categories():
    """List all available categories with their slugs"""
    return {
        "total": len(CATEGORIES),
        "categories": [
            {
                "slug": slug,
                "id": cat_id,
                "name": CATEGORY_NAMES.get(cat_id, slug.title())
            }
            for slug, cat_id in CATEGORIES.items()
        ]
    }


@app.get("/api/v1/{geo}")
async def get_all_trends(
    geo: str,
    workers: int = 3
):
    """
    Get ALL trends from ALL categories as a flat list
    
    Parameters:
    - geo: Country code (IN, US, GB, etc.)
    - workers: Number of parallel workers (1-5, default: 3)
    
    Returns flat array where each trend includes category field
    """
    geo = geo.upper()
    workers = min(max(workers, 1), 5)  # Limit 1-5
    
    # Check cache
    cache_key = get_cache_key(geo)
    cached_data = get_from_cache(cache_key)
    
    if cached_data:
        cached_data["cached"] = True
        return JSONResponse(content=cached_data)
    
    logger.info(f"Fetching all trends for {geo} with {workers} workers")
    start_time = time.time()
    
    all_trends = []
    successful = 0
    failed = 0
    empty = 0
    
    def fetch_category(category_id: int, category_name: str):
        """Fetch single category"""
        url = f"https://trends.google.com/trending?geo={geo}&category={category_id}"
        data = scrape_google_trends(url, category_name, category_id)
        
        if data:
            return {"status": "success", "id": category_id, "name": category_name, "data": data}
        else:
            return {"status": "failed", "id": category_id, "name": category_name, "data": []}
    
    # Parallel scraping
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(fetch_category, cat_id, cat_name): cat_name
            for cat_id, cat_name in CATEGORY_NAMES.items()
        }
        
        for future in as_completed(futures):
            try:
                result = future.result()
                
                if result["status"] == "success":
                    successful += 1
                    # Add category to each trend
                    for trend in result["data"]:
                        all_trends.append({
                            "category": result["name"],
                            "category_id": result["id"],
                            **trend
                        })
                else:
                    if result["data"] == []:
                        empty += 1
                    else:
                        failed += 1
            except Exception as e:
                logger.error(f"Error in future: {e}")
                failed += 1
    
    execution_time = time.time() - start_time
    
    response = {
        "geo": geo,
        "total_categories": len(CATEGORY_NAMES),
        "successful_categories": successful,
        "failed_categories": failed,
        "empty_categories": empty,
        "total_trends": len(all_trends),
        "trends": all_trends,
        "timestamp": datetime.now().isoformat(),
        "execution_time": round(execution_time, 2),
        "cached": False
    }
    
    # Cache response
    set_cache(cache_key, response)
    
    logger.info(f"Completed {geo}: {len(all_trends)} trends in {execution_time:.2f}s")
    return JSONResponse(content=response)


@app.get("/api/v1/{geo}/{category}")
async def get_category_trends(geo: str, category: str):
    """
    Get trends for a specific category
    
    Parameters:
    - geo: Country code (IN, US, GB, etc.)
    - category: Category slug (business, technology, sports, etc.)
    
    See /categories for all available categories
    """
    geo = geo.upper()
    category = category.lower()
    
    # Validate category
    if category not in CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category '{category}'. Use /categories to see available options."
        )
    
    category_id = CATEGORIES[category]
    category_name = CATEGORY_NAMES[category_id]
    
    # Check cache
    cache_key = get_cache_key(geo, category)
    cached_data = get_from_cache(cache_key)
    
    if cached_data:
        cached_data["cached"] = True
        return JSONResponse(content=cached_data)
    
    logger.info(f"Fetching {category} trends for {geo}")
    
    # Scrape
    url = f"https://trends.google.com/trending?geo={geo}&category={category_id}"
    data = scrape_google_trends(url, category_name, category_id)
    
    if data is None:
        raise HTTPException(
            status_code=404,
            detail=f"No trends found for category '{category}' in {geo}. Category might be empty."
        )
    
    response = {
        "geo": geo,
        "category": category_name,
        "category_id": category_id,
        "category_slug": category,
        "total_trends": len(data),
        "trends": data,
        "timestamp": datetime.now().isoformat(),
        "cached": False
    }
    
    # Cache response
    set_cache(cache_key, response)
    
    logger.info(f"Found {len(data)} trends for {category} in {geo}")
    return JSONResponse(content=response)


@app.delete("/cache")
async def clear_cache():
    """Clear all cached data (admin endpoint)"""
    with cache_lock:
        count = len(cache)
        cache.clear()
    logger.info(f"Cache cleared: {count} entries removed")
    return {"message": f"Cache cleared ({count} entries removed)"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
