"""
Carbon intensity service for Project-C12.
"""

import logging
import aiohttp
from datetime import datetime
import random
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_CARBON_INTENSITY = 300  # gCO2/kWh
MOCK_MODE = True  # Set to True for development without API key
CACHE_DURATION = 300  # 5 minutes

# API configuration
ELECTRICITY_MAP_API_KEY = "KnVGxwFL5wrrbWJeA4NO"  # Hardcode the API key for now
ELECTRICITY_MAP_ZONE = "IN-NO"  # Northern region of India

# Disable mock mode and use live API
MOCK_MODE = False

# API endpoints
API_BASE_URL = "https://api.electricitymap.org/v3"

class CarbonService:
    """Service for managing carbon intensity data."""
    
    def __init__(self):
        """Initialize the carbon service."""
        self._last_update = None
        self._last_value = DEFAULT_CARBON_INTENSITY
        self._error_count = 0
        self._session = None
        self._max_retries = 3  # Maximum number of retries before considering service unhealthy
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
            
    async def close(self):
        """Close the aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None
        self._max_retries = 3
        
    async def get_mock_intensity(self) -> dict:
        """Get mock carbon intensity data for development."""
        now = datetime.now()
        
        # Simulate daily carbon intensity pattern
        hour = now.hour
        base = 250  # Base carbon intensity
        
        # Higher during peak hours (morning and evening)
        if 7 <= hour <= 10:  # Morning peak
            base += 100
        elif 18 <= hour <= 22:  # Evening peak
            base += 150
        elif 0 <= hour <= 5:  # Night time (low usage)
            base -= 50
            
        # Add some randomness
        variation = random.randint(-30, 30)
        intensity = max(50, min(600, base + variation))
        
        # Update cache
        self._last_value = intensity
        self._last_update = now
        
        return {
            "carbon_intensity": intensity,
            "status": "mock",
            "last_update": now,
            "error": None
        }
        
    async def get_carbon_intensity(self) -> dict:
        """
        Get current carbon intensity with status.
        
        Returns:
            Dict with carbon intensity and status information
        """
        try:
            # Use mock data if no API key
            if MOCK_MODE or not ELECTRICITY_MAP_API_KEY:
                return await self.get_mock_intensity()
            
            # Check cache
            now = datetime.now()
            if (self._last_update and 
                (now - self._last_update).total_seconds() < CACHE_DURATION):
                return {
                    "carbon_intensity": self._last_value,
                    "status": "cached",
                    "last_update": self._last_update,
                    "error": None
                }
            
            try:
                # Fetch new data
                async with aiohttp.ClientSession() as session:
                    # Construct URL
                    url = f"{API_BASE_URL}/carbon-intensity/latest"
                    
                    # Set headers
                    headers = {
                        "auth-token": ELECTRICITY_MAP_API_KEY,
                        "Accept": "application/json"
                    }
                    
                    # Set query parameters
                    params = {"zone": ELECTRICITY_MAP_ZONE}
                    
                    logger.info(f"Fetching carbon intensity for zone {ELECTRICITY_MAP_ZONE}")
                    async with session.get(url, headers=headers, params=params, timeout=10) as response:
                        response_text = await response.text()
                        logger.info(f"Raw API response: {response_text}")
                        
                        if response.status != 200:
                            raise Exception(f"API returned status {response.status}: {response_text}")
                        
                        try:
                            data = await response.json()
                            logger.info(f"Raw API response: {data}")
                            
                            # Extract values from response
                            intensity = int(data.get("carbonIntensity", DEFAULT_CARBON_INTENSITY))
                            updated_at = datetime.fromisoformat(data["updatedAt"].replace('Z', '+00:00'))
                            is_estimated = data.get("isEstimated", True)
                            
                            # Update cache
                            self._last_value = intensity
                            self._last_update = now
                            self._error_count = 0
                            
                            logger.info(f"Got carbon intensity: {intensity} gCO2/kWh (updated at {updated_at}, estimated: {is_estimated})")
                            return {
                                "carbon_intensity": intensity,
                                "status": "live",
                                "last_update": updated_at,
                                "updated_at": updated_at,
                                "is_estimated": is_estimated,
                                "error": None,
                                "zone": data.get("zone")
                            }
                        except (ValueError, KeyError) as e:
                            raise Exception(f"Invalid API response format: {str(e)}")
                            
            except aiohttp.ClientError as e:
                raise Exception(f"API request failed: {str(e)}")
            except Exception as e:
                logger.error(f"Error fetching carbon intensity: {str(e)}")
                raise
                    
        except Exception as e:
            self._error_count += 1
            error_msg = f"Failed to fetch carbon intensity: {str(e)}"
            logger.error(error_msg)
            
            # If we have recent cached data, use it
            if self._last_update and (now - self._last_update).total_seconds() < 3600:
                return {
                    "carbon_intensity": self._last_value,
                    "status": "cached",
                    "last_update": self._last_update,
                    "error": error_msg
                }
            
            # Fallback to default
            return {
                "carbon_intensity": DEFAULT_CARBON_INTENSITY,
                "status": "error",
                "last_update": None,
                "error": error_msg
            }
    
    @property
    def is_healthy(self) -> bool:
        """Check if the service is healthy."""
        # Service is healthy if:
        # 1. We have a valid API key
        # 2. Error count is below max retries
        # 3. Last update is recent (within last hour) if we have one
        now = datetime.now()
        recent_update = True if not self._last_update else (now - self._last_update).total_seconds() < 3600
        
        return bool(ELECTRICITY_MAP_API_KEY) and self._error_count < self._max_retries and recent_update
    
    @property
    def last_update(self) -> datetime:
        """Get last successful update time."""
        return self._last_update