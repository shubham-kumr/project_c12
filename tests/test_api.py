"""
Test suite for Project-C12 API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_root_endpoint():
    """
    Test the root endpoint.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "Project-C12 API"

def test_health_endpoint():
    """
    Test the health check endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["carbon_aware"] is True

def test_invalid_endpoint():
    """
    Test response for invalid endpoint.
    """
    response = client.get("/invalid")
    assert response.status_code == 404 