"""
Unit tests for the routing service.
"""

import pytest
from datetime import datetime
from src.api.services.routing import RoutingService
from src.api.services.carbon import CarbonService
from src.api.services.model import ModelService
from src.api.services.optimization import OptimizationService

@pytest.fixture
def carbon_service():
    """Mock carbon service fixture."""
    class MockCarbonService:
        async def get_carbon_intensity(self, region=None):
            return {
                "carbon_intensity": 0.5,
                "timestamp": datetime.utcnow().isoformat(),
                "region": region or "default"
            }
    return MockCarbonService()

@pytest.fixture
def model_service():
    """Mock model service fixture."""
    class MockModelService:
        def get_available_models(self):
            return [
                {
                    "model_id": "gpt2-small",
                    "carbon_footprint_per_inference": 0.1,
                    "performance_score": 0.8
                },
                {
                    "model_id": "gpt2-medium",
                    "carbon_footprint_per_inference": 0.2,
                    "performance_score": 0.9
                }
            ]
            
        def get_model_info(self, model_id):
            return {
                "model_id": model_id,
                "parameters": 1000000,
                "carbon_footprint_per_inference": 0.1,
                "performance_score": 0.8
            }
    return MockModelService()

@pytest.fixture
def optimization_service():
    """Mock optimization service fixture."""
    class MockOptimizationService:
        def recommend_strategy(self, base_carbon, base_performance, performance_threshold):
            return {
                "strategy_id": "quantization",
                "carbon_reduction": 0.4,
                "performance_impact": -0.1
            }
    return MockOptimizationService()

@pytest.fixture
def routing_service(carbon_service, model_service, optimization_service):
    """Routing service fixture."""
    return RoutingService(carbon_service, model_service, optimization_service)

@pytest.mark.asyncio
async def test_select_model(routing_service):
    """Test model selection with valid parameters."""
    result = await routing_service.select_model(
        task_complexity=0.5,
        performance_threshold=0.7
    )
    
    assert "model" in result
    assert "optimization" in result
    assert "carbon_intensity" in result
    assert "selection_metrics" in result
    
    assert result["selection_metrics"]["performance_score"] >= 0.7
    assert result["optimization"]["strategy_id"] == "quantization"

@pytest.mark.asyncio
async def test_select_model_with_region(routing_service):
    """Test model selection with region parameter."""
    result = await routing_service.select_model(
        task_complexity=0.5,
        performance_threshold=0.7,
        region="us-west"
    )
    
    assert result["carbon_intensity"]["region"] == "us-west"

@pytest.mark.asyncio
async def test_select_model_invalid_complexity(routing_service):
    """Test model selection with invalid task complexity."""
    with pytest.raises(ValueError):
        await routing_service.select_model(
            task_complexity=1.5,
            performance_threshold=0.7
        )

def test_get_request_history(routing_service):
    """Test getting request history."""
    history = routing_service.get_request_history()
    assert isinstance(history, list)

def test_get_performance_metrics_empty(routing_service):
    """Test getting performance metrics with empty history."""
    metrics = routing_service.get_performance_metrics()
    assert metrics["total_requests"] == 0
    assert metrics["average_carbon_savings"] == 0
    assert metrics["average_performance_score"] == 0

@pytest.mark.asyncio
async def test_get_performance_metrics_with_requests(routing_service):
    """Test getting performance metrics with request history."""
    # Make some requests
    await routing_service.select_model(task_complexity=0.5)
    await routing_service.select_model(task_complexity=0.6)
    
    metrics = routing_service.get_performance_metrics()
    assert metrics["total_requests"] == 2
    assert metrics["average_carbon_savings"] > 0
    assert metrics["average_performance_score"] > 0 