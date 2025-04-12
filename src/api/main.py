"""
Main FastAPI application for Project-C12.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
import logging

from src.api.services.model import ModelService
from src.api.services.carbon import CarbonService, ELECTRICITY_MAP_ZONE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Project-C12 API")

# Initialize services
model_service = ModelService()
carbon_service = CarbonService()

class Query(BaseModel):
    """Query model for API requests."""
    text: str
    max_length: Optional[int] = 512
    model: Optional[str] = 'auto'  # Added model selection

@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    await model_service.initialize()

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status of all services
    """
    carbon_data = await carbon_service.get_carbon_intensity()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "model": model_service._last_update is not None,
            "carbon": {
                "status": carbon_data["status"],
                "healthy": carbon_service.is_healthy,
                "last_update": carbon_data["last_update"].isoformat() if carbon_data["last_update"] else None,
                "error": carbon_data["error"]
            }
        }
    }

@app.get("/api/carbon-intensity")
async def get_carbon_intensity():
    """
    Get current carbon intensity.
    
    Returns:
        Current carbon intensity data
    """
    try:
        carbon_data = await carbon_service.get_carbon_intensity()
        
        # Check service health
        if not carbon_service.is_healthy:
            raise HTTPException(
                status_code=503,
                detail="Carbon intensity service is unhealthy"
            )
        
        # Check for error status
        if carbon_data["status"] == "error":
            raise HTTPException(
                status_code=503,
                detail=f"Error fetching carbon intensity: {carbon_data['error']}"
            )
        
        # Format the response
        response = {
            "carbon_intensity": carbon_data["carbon_intensity"],
            "status": carbon_data["status"],
            "online": True,
            "zone": carbon_data.get("zone", ELECTRICITY_MAP_ZONE),
            "is_estimated": carbon_data.get("is_estimated", True),
            "last_update": carbon_data["last_update"].isoformat() if carbon_data["last_update"] else None
        }
        
        # Add additional metadata if available
        if carbon_data.get("updated_at"):
            response["updated_at"] = carbon_data["updated_at"].isoformat()
            
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in carbon intensity endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

from asyncio import TimeoutError as AsyncTimeoutError
from asyncio import wait_for

@app.post("/api/ask")
async def ask_query(query: Query):
    """
    Process a query using the carbon-aware model router.
    
    Args:
        query: Query model with text and optional parameters
        
    Returns:
        Model response
    """
    try:
        # Get carbon intensity
        carbon_data = await carbon_service.get_carbon_intensity()
        carbon_intensity = carbon_data["carbon_intensity"]
        
        try:
            # Handle model selection with timeout
            if query.model == 'auto':
                model_name = await wait_for(
                    model_service.select_model(query.text, carbon_intensity),
                    timeout=10.0  # 10 second timeout for model selection
                )
            else:
                model_name = query.model
                
            # Log selected model and query info
            logger.info(
                f"Model: {model_name} ({'auto-selected' if query.model == 'auto' else 'manually selected'}) "
                f"for query: {query.text[:50]}..."
            )
            
            # Generate response with timeout
            response = await wait_for(
                model_service.generate_response(
                    model_name,
                    query.text,
                    query.max_length
                ),
                timeout=90.0  # 90 second timeout for response generation
            )
            
        except AsyncTimeoutError:
            logger.error(f"Timeout processing query: {query.text[:50]}...")
            raise HTTPException(
                status_code=504,
                detail="Request timed out. The model is taking too long to respond."
            )
        
        return {
            "response": response,
            "model": model_name,
            "carbon_intensity": carbon_intensity,
            "carbon_status": carbon_data["status"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)