"""
Data validation module for the Project-C12 dashboard.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_carbon_intensity(data: Dict) -> Dict:
    """
    Validate carbon intensity data structure.
    
    Args:
        data: Dictionary containing carbon intensity data
        
    Returns:
        Validated carbon intensity data
        
    Raises:
        ValidationError: If data is invalid
    """
    if not isinstance(data, dict):
        raise ValidationError("Carbon intensity data must be a dictionary")
    
    required_fields = ["carbon_intensity", "timestamp", "region"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    if not isinstance(data["carbon_intensity"], (int, float)):
        raise ValidationError("Carbon intensity must be a number")
    
    if data["carbon_intensity"] < 0:
        raise ValidationError("Carbon intensity cannot be negative")
    
    try:
        datetime.fromisoformat(data["timestamp"])
    except (ValueError, TypeError):
        raise ValidationError("Invalid timestamp format")
    
    return data

def validate_model_data(data: Dict) -> Dict:
    """
    Validate model data structure.
    
    Args:
        data: Dictionary containing model data
        
    Returns:
        Validated model data
        
    Raises:
        ValidationError: If data is invalid
    """
    if not isinstance(data, dict):
        raise ValidationError("Model data must be a dictionary")
    
    required_fields = ["model_id", "name", "parameters", "carbon_footprint", "performance_score"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    if not isinstance(data["parameters"], int):
        raise ValidationError("Model parameters must be an integer")
    
    if not isinstance(data["carbon_footprint"], (int, float)):
        raise ValidationError("Carbon footprint must be a number")
    
    if not isinstance(data["performance_score"], (int, float)):
        raise ValidationError("Performance score must be a number")
    
    if not 0 <= data["performance_score"] <= 1:
        raise ValidationError("Performance score must be between 0 and 1")
    
    return data

def validate_optimization_data(data: Dict) -> Dict:
    """
    Validate optimization strategy data structure.
    
    Args:
        data: Dictionary containing optimization data
        
    Returns:
        Validated optimization data
        
    Raises:
        ValidationError: If data is invalid
    """
    if not isinstance(data, dict):
        raise ValidationError("Optimization data must be a dictionary")
    
    required_fields = ["strategy_id", "carbon_reduction", "performance_impact"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    if not isinstance(data["carbon_reduction"], (int, float)):
        raise ValidationError("Carbon reduction must be a number")
    
    if not isinstance(data["performance_impact"], (int, float)):
        raise ValidationError("Performance impact must be a number")
    
    if not 0 <= data["carbon_reduction"] <= 1:
        raise ValidationError("Carbon reduction must be between 0 and 1")
    
    if not -1 <= data["performance_impact"] <= 1:
        raise ValidationError("Performance impact must be between -1 and 1")
    
    return data

def validate_performance_metrics(data: Dict) -> Dict:
    """
    Validate performance metrics data structure.
    
    Args:
        data: Dictionary containing performance metrics
        
    Returns:
        Validated performance metrics
        
    Raises:
        ValidationError: If data is invalid
    """
    if not isinstance(data, dict):
        raise ValidationError("Performance metrics must be a dictionary")
    
    required_fields = ["total_requests", "average_carbon_savings", "average_performance_score"]
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    if not isinstance(data["total_requests"], int):
        raise ValidationError("Total requests must be an integer")
    
    if not isinstance(data["average_carbon_savings"], (int, float)):
        raise ValidationError("Average carbon savings must be a number")
    
    if not isinstance(data["average_performance_score"], (int, float)):
        raise ValidationError("Average performance score must be a number")
    
    if data["total_requests"] < 0:
        raise ValidationError("Total requests cannot be negative")
    
    if not 0 <= data["average_carbon_savings"] <= 1:
        raise ValidationError("Average carbon savings must be between 0 and 1")
    
    if not 0 <= data["average_performance_score"] <= 1:
        raise ValidationError("Average performance score must be between 0 and 1")
    
    return data

def validate_input_parameters(
    task_complexity: float,
    performance_threshold: float,
    region: str
) -> None:
    """
    Validate input parameters for model selection.
    
    Args:
        task_complexity: Task complexity score (0-1)
        performance_threshold: Performance threshold (0-1)
        region: Target region
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if not isinstance(task_complexity, (int, float)):
        raise ValidationError("Task complexity must be a number")
    
    if not isinstance(performance_threshold, (int, float)):
        raise ValidationError("Performance threshold must be a number")
    
    if not isinstance(region, str):
        raise ValidationError("Region must be a string")
    
    if not 0 <= task_complexity <= 1:
        raise ValidationError("Task complexity must be between 0 and 1")
    
    if not 0 <= performance_threshold <= 1:
        raise ValidationError("Performance threshold must be between 0 and 1")
    
    if not region:
        raise ValidationError("Region cannot be empty") 