"""
Pydantic schemas for the router API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class ModelSelectionRequest(BaseModel):
    """
    Request schema for model selection.
    """
    task_complexity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Complexity score of the task (0-1)"
    )
    performance_threshold: float = Field(
        0.7,
        ge=0.0,
        le=1.0,
        description="Minimum acceptable performance score"
    )
    region: Optional[str] = Field(
        None,
        description="Optional region for carbon intensity lookup"
    )

class ModelSelectionResponse(BaseModel):
    """
    Response schema for model selection.
    """
    model: Dict = Field(
        ...,
        description="Selected model information"
    )
    optimization: Dict = Field(
        ...,
        description="Recommended optimization strategy"
    )
    carbon_intensity: Dict = Field(
        ...,
        description="Current carbon intensity data"
    )
    selection_metrics: Dict = Field(
        ...,
        description="Metrics used for model selection"
    )

class RequestHistoryEntry(BaseModel):
    """
    Schema for a request history entry.
    """
    timestamp: datetime = Field(
        ...,
        description="Timestamp of the request"
    )
    model_id: str = Field(
        ...,
        description="ID of the selected model"
    )
    carbon_intensity: Dict = Field(
        ...,
        description="Carbon intensity at the time of selection"
    )
    task_complexity: float = Field(
        ...,
        description="Complexity of the task"
    )
    performance_threshold: float = Field(
        ...,
        description="Performance threshold used"
    )
    optimization_strategy: str = Field(
        ...,
        description="Optimization strategy applied"
    )
    carbon_savings: float = Field(
        ...,
        description="Estimated carbon savings"
    )

class RequestHistoryResponse(BaseModel):
    """
    Response schema for request history.
    """
    requests: List[RequestHistoryEntry] = Field(
        ...,
        description="List of recent request history entries"
    )

class PerformanceMetricsResponse(BaseModel):
    """
    Response schema for performance metrics.
    """
    total_requests: int = Field(
        ...,
        description="Total number of requests processed"
    )
    average_carbon_savings: float = Field(
        ...,
        description="Average carbon savings per request"
    )
    average_performance_score: float = Field(
        ...,
        description="Average performance score achieved"
    ) 