"""
Tests for the Streamlit dashboard.
"""

import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
from src.dashboard.app import (
    fetch_carbon_intensity,
    fetch_available_models,
    fetch_performance_metrics,
    select_model
)

@pytest.fixture
def mock_httpx():
    """Mock httpx client fixture."""
    with patch("src.dashboard.app.httpx") as mock:
        yield mock

def test_fetch_carbon_intensity(mock_httpx):
    """Test fetching carbon intensity data."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "carbon_intensity": 0.5,
        "timestamp": "2024-03-20T12:00:00Z",
        "region": "us-west"
    }
    mock_httpx.get.return_value = mock_response
    
    result = fetch_carbon_intensity()
    assert result["carbon_intensity"] == 0.5
    assert result["region"] == "us-west"

def test_fetch_available_models(mock_httpx):
    """Test fetching available models."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "models": [
            {
                "model_id": "gpt2-small",
                "carbon_footprint_per_inference": 0.1,
                "performance_score": 0.8
            }
        ]
    }
    mock_httpx.get.return_value = mock_response
    
    result = fetch_available_models()
    assert len(result) == 1
    assert result[0]["model_id"] == "gpt2-small"

def test_fetch_performance_metrics(mock_httpx):
    """Test fetching performance metrics."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "total_requests": 100,
        "average_carbon_savings": 0.3,
        "average_performance_score": 0.8
    }
    mock_httpx.get.return_value = mock_response
    
    result = fetch_performance_metrics()
    assert result["total_requests"] == 100
    assert result["average_carbon_savings"] == 0.3

def test_select_model(mock_httpx):
    """Test model selection."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": {
            "model_id": "gpt2-small",
            "parameters": 1000000,
            "performance_score": 0.8
        },
        "optimization": {
            "strategy_id": "quantization",
            "carbon_reduction": 0.4,
            "performance_impact": -0.1
        }
    }
    mock_httpx.post.return_value = mock_response
    
    result = select_model(
        task_complexity=0.5,
        performance_threshold=0.7,
        region="us-west"
    )
    
    assert result["model"]["model_id"] == "gpt2-small"
    assert result["optimization"]["strategy_id"] == "quantization"

def test_error_handling(mock_httpx):
    """Test error handling in API calls."""
    mock_httpx.get.side_effect = Exception("API Error")
    
    # Test carbon intensity fetch
    result = fetch_carbon_intensity()
    assert result is None
    
    # Test models fetch
    result = fetch_available_models()
    assert result == []
    
    # Test metrics fetch
    result = fetch_performance_metrics()
    assert result is None
    
    # Test model selection
    mock_httpx.post.side_effect = Exception("API Error")
    result = select_model(0.5, 0.7, "us-west")
    assert result is None 