"""
Utility functions for the dashboard.
"""

import httpx
from typing import Dict, List, Optional
from src.dashboard.validation import (
    validate_carbon_intensity,
    validate_model_data,
    validate_optimization_data,
    validate_performance_metrics,
    ValidationError
)

API_BASE_URL = "http://localhost:8000/api"

def show_error(message: str, details: Optional[str] = None) -> None:
    """
    Display an error message with optional details.
    
    Args:
        message: Main error message
        details: Optional detailed error information
    """
    import streamlit as st
    st.error(message)
    if details:
        with st.expander("Error Details"):
            st.code(details)

def fetch_carbon_intensity() -> Optional[Dict]:
    """
    Fetch current carbon intensity data.
    
    Returns:
        Validated carbon intensity data or None if error occurs
    """
    try:
        response = httpx.get(f"{API_BASE_URL}/carbon/intensity")
        data = response.json()
        return validate_carbon_intensity(data)
    except ValidationError as e:
        show_error("Invalid carbon intensity data", str(e))
        return None
    except Exception as e:
        show_error("Error fetching carbon intensity", str(e))
        return None

def fetch_available_models() -> List[Dict]:
    """
    Fetch available models from the API.
    
    Returns:
        List of validated model data
    """
    try:
        response = httpx.get(f"{API_BASE_URL}/models")
        data = response.json()
        if "models" not in data:
            show_error("Invalid models data format")
            return []
            
        models = data["models"]
        validated_models = []
        for model in models:
            try:
                validated_models.append(validate_model_data(model))
            except ValidationError as e:
                show_error(f"Invalid model data: {model.get('model_id', 'unknown')}", str(e))
        return validated_models
    except Exception as e:
        show_error("Error fetching models", str(e))
        return []

def fetch_performance_metrics() -> Optional[Dict]:
    """
    Fetch performance metrics from the API.
    
    Returns:
        Validated performance metrics or None if error occurs
    """
    try:
        response = httpx.get(f"{API_BASE_URL}/router/performance-metrics")
        data = response.json()
        return validate_performance_metrics(data)
    except ValidationError as e:
        show_error("Invalid performance metrics data", str(e))
        return None
    except Exception as e:
        show_error("Error fetching performance metrics", str(e))
        return None

def select_model(task_complexity: float, performance_threshold: float, region: str) -> Optional[Dict]:
    """
    Select the most carbon-efficient model.
    
    Args:
        task_complexity: Complexity of the task (0-1)
        performance_threshold: Minimum acceptable performance (0-1)
        region: Target region for carbon intensity
        
    Returns:
        Model selection result or None if error occurs
    """
    try:
        response = httpx.post(
            f"{API_BASE_URL}/router/select-model",
            json={
                "task_complexity": task_complexity,
                "performance_threshold": performance_threshold,
                "region": region
            }
        )
        data = response.json()
        
        # Validate the response structure
        if "model" not in data or "optimization" not in data:
            raise ValidationError("Invalid model selection response")
            
        data["model"] = validate_model_data(data["model"])
        data["optimization"] = validate_optimization_data(data["optimization"])
        
        return data
    except ValidationError as e:
        show_error("Invalid model selection data", str(e))
        return None
    except Exception as e:
        show_error("Error selecting model", str(e))
        return None 