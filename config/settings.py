"""
Configuration settings for Google Trends API v2.0
With background fetching support
"""
import os
from typing import List

class Settings:
    # API Settings
    API_TITLE = "Google Trends API"
    API_VERSION = "2.0.0"
    API_DESCRIPTION = "Production-ready API with background data fetching"
    
    # Server Settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    RELOAD = os.getenv("RELOAD", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
    
    # Background Fetch Settings
    REFRESH_INTERVAL_MINUTES = int(os.getenv("REFRESH_INTERVAL_MINUTES", 30))
    DEFAULT_GEOS = os.getenv("DEFAULT_GEOS", "IN,US,GB,AU,CA").split(",")
    
    # Cache Settings
    CACHE_DIR = os.getenv("CACHE_DIR", "cache_data")
    
    # Scraping Settings
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", 1))  # Sequential for stability
    DOWNLOAD_TIMEOUT = int(os.getenv("DOWNLOAD_TIMEOUT", 40))
    
    # CORS Settings
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Temp directory
    TEMP_DIR = os.getenv("TEMP_DIR", "temp_downloads")

settings = Settings()
