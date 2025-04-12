"""
API routes for the routing service.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from ..services.routing import RoutingService
from ..services.carbon import CarbonService
from ..services.model import ModelService
from ..services.optimization import OptimizationService
from ..schemas.router import (
    ModelSelectionRequest,
    ModelSelectionResponse,
    RequestHistoryResponse,
    PerformanceMetricsResponse
)

router = APIRouter(prefix="/router", tags=["router"])

def get_routing_service(
    carbon_service: CarbonService = Depends(),
    model_service: ModelService = Depends(),
    optimization_service: OptimizationService = Depends()
) -> RoutingService:
    """Dependency injection for routing service."""
    return RoutingService(carbon_service, model_service, optimization_service)

@router.post("/select-model", response_model=ModelSelectionResponse)
async def select_model(
    request: ModelSelectionRequest,
    routing_service: RoutingService = Depends(get_routing_service)
):
    """
    Select the most carbon-efficient model for a given task.
    
    Args:
        request: Model selection request containing task complexity and preferences
        
    Returns:
        Model selection response with selected model and optimization strategy
    """
    try:
        return await routing_service.select_model(
            task_complexity=request.task_complexity,
            performance_threshold=request.performance_threshold,
            region=request.region
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/request-history", response_model=RequestHistoryResponse)
async def get_request_history(
    limit: Optional[int] = 100,
    routing_service: RoutingService = Depends(get_routing_service)
):
    """
    Get recent request history.
    
    Args:
        limit: Maximum number of requests to return
        
    Returns:
        List of recent request history entries
    """
    return {"requests": routing_service.get_request_history(limit)}

@router.get("/performance-metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    routing_service: RoutingService = Depends(get_routing_service)
):
    """
    Get performance metrics based on request history.
    
    Returns:
        Performance metrics including total requests and averages
    """
    return routing_service.get_performance_metrics() 