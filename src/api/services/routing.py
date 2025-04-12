"""
Routing service for selecting the optimal model based on carbon intensity and performance.
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging
from .carbon import CarbonService
from .model import ModelService
from .optimization import OptimizationService

logger = logging.getLogger(__name__)

class RoutingService:
    """
    Service for routing inference requests to the most carbon-efficient model.
    """
    
    def __init__(
        self,
        carbon_service: CarbonService,
        model_service: ModelService,
        optimization_service: OptimizationService
    ):
        """
        Initialize the routing service.
        
        Args:
            carbon_service: Instance of CarbonService
            model_service: Instance of ModelService
            optimization_service: Instance of OptimizationService
        """
        self.carbon_service = carbon_service
        self.model_service = model_service
        self.optimization_service = optimization_service
        self.request_history: List[Dict] = []
        
    async def select_model(
        self,
        task_complexity: float,
        performance_threshold: float = 0.7,
        region: Optional[str] = None
    ) -> Dict:
        """
        Select the most carbon-efficient model for a given task.
        
        Args:
            task_complexity: Complexity score of the task (0-1)
            performance_threshold: Minimum acceptable performance score
            region: Optional region for carbon intensity lookup
            
        Returns:
            Dict containing selected model and optimization strategy
        """
        try:
            # Get current carbon intensity
            carbon_intensity = await self.carbon_service.get_carbon_intensity(region)
            
            # Get available models
            available_models = self.model_service.get_available_models()
            
            # Calculate scores for each model
            model_scores = []
            for model in available_models:
                # Calculate carbon impact
                carbon_impact = (
                    model["carbon_footprint_per_inference"] *
                    carbon_intensity["carbon_intensity"]
                )
                
                # Calculate performance score
                performance_score = model["performance_score"]
                
                # Calculate overall score
                score = (
                    (1 - carbon_impact) * 0.6 +  # Carbon impact weight: 60%
                    performance_score * 0.4       # Performance weight: 40%
                )
                
                model_scores.append({
                    "model_id": model["model_id"],
                    "score": score,
                    "carbon_impact": carbon_impact,
                    "performance_score": performance_score
                })
            
            # Sort models by score
            model_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # Select the best model that meets performance threshold
            selected_model = None
            for model_score in model_scores:
                if model_score["performance_score"] >= performance_threshold:
                    selected_model = model_score
                    break
            
            if not selected_model:
                raise ValueError("No suitable model found for the given requirements")
            
            # Get model info
            model_info = self.model_service.get_model_info(selected_model["model_id"])
            
            # Get optimization recommendation
            optimization = self.optimization_service.recommend_strategy(
                base_carbon=selected_model["carbon_impact"],
                base_performance=selected_model["performance_score"],
                performance_threshold=performance_threshold
            )
            
            # Log the selection
            selection = {
                "timestamp": datetime.utcnow().isoformat(),
                "model_id": selected_model["model_id"],
                "carbon_intensity": carbon_intensity,
                "task_complexity": task_complexity,
                "performance_threshold": performance_threshold,
                "optimization_strategy": optimization["strategy_id"],
                "carbon_savings": optimization["carbon_reduction"]
            }
            self.request_history.append(selection)
            logger.info(f"Model selected: {selection}")
            
            return {
                "model": model_info,
                "optimization": optimization,
                "carbon_intensity": carbon_intensity,
                "selection_metrics": {
                    "carbon_impact": selected_model["carbon_impact"],
                    "performance_score": selected_model["performance_score"],
                    "overall_score": selected_model["score"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error selecting model: {str(e)}")
            raise
            
    def get_request_history(self, limit: int = 100) -> List[Dict]:
        """
        Get recent request history.
        
        Args:
            limit: Maximum number of requests to return
            
        Returns:
            List of recent request history entries
        """
        return self.request_history[-limit:]
        
    def get_performance_metrics(self) -> Dict:
        """
        Calculate performance metrics based on request history.
        
        Returns:
            Dict containing performance metrics
        """
        if not self.request_history:
            return {
                "total_requests": 0,
                "average_carbon_savings": 0,
                "average_performance_score": 0
            }
            
        total_requests = len(self.request_history)
        total_carbon_savings = sum(
            request["carbon_savings"] for request in self.request_history
        )
        total_performance = sum(
            request["performance_threshold"] for request in self.request_history
        )
        
        return {
            "total_requests": total_requests,
            "average_carbon_savings": total_carbon_savings / total_requests,
            "average_performance_score": total_performance / total_requests
        } 