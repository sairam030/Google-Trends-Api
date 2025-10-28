"""
Configuration settings for Google Trends API
"""
import os
from typing import List

class Settings:
    # API Settings
    API_TITLE = "Google Trends API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "Production-ready API for real-time Google Trends data"
    
    # Server Settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    RELOAD = os.getenv("RELOAD", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
    
    # Cache Settings
    CACHE_TTL = int(os.getenv("CACHE_TTL", 3600))  # 1 hour default
    
    # Scraping Settings
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", 5))
    DOWNLOAD_TIMEOUT = int(os.getenv("DOWNLOAD_TIMEOUT", 40))
    
    # CORS Settings
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Temp directory
    TEMP_DIR = os.getenv("TEMP_DIR", "temp_downloads")

settings = Settings()
