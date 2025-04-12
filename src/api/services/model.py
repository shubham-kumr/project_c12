"""
Model service for Project-C12.
"""

import os
import logging
from typing import Dict, Optional
from datetime import datetime
from async_timeout import timeout as async_timeout

from llama_cpp import Llama
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
TINYLLAMA_PATH = os.path.join(MODELS_DIR, "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
GPT2_PATH = "gpt2"  # Will be downloaded from HuggingFace
CODELLAMA_PATH = "TheBloke/CodeLlama-7B-GGUF"  # Quantized model ID

# Model characteristics
MODEL_INFO = {
    "tinyllama": {
        "size": "small",
        "energy": 0.001,  # kWh per 1k tokens
        "capabilities": ["general", "qa", "classification"],
        "max_tokens": 2048
    },
    "gpt2": {
        "size": "medium",
        "energy": 0.01,
        "capabilities": ["general", "qa", "analysis"],
        "max_tokens": 1024
    },
    "codellama": {
        "size": "large",
        "energy": 0.02,
        "capabilities": ["code", "analysis", "technical"],
        "max_tokens": 4096
    }
}

# Carbon thresholds (gCO2/kWh)
CARBON_THRESHOLDS = {
    "low": 100,    # Use any model
    "medium": 300, # Prefer efficient models
    "high": 500    # Use only TinyLlama
}

# Query complexity indicators
COMPLEX_KEYWORDS = {
    "analyze", "explain", "compare", "evaluate", "synthesize",
    "technical", "detailed", "in-depth", "comprehensive"
}

# Code-related keywords by category
CODE_KEYWORDS = {
    'general': {
        'code', 'program', 'function', 'class', 'algorithm', 'implement',
        'debug', 'fix', 'error', 'bug', 'compile', 'runtime', 'syntax'
    },
    'languages': {
        'python', 'javascript', 'typescript', 'java', 'c++', 'cpp', 'rust',
        'go', 'html', 'css', 'sql', 'php', 'swift', 'kotlin'
    },
    'concepts': {
        'array', 'string', 'list', 'dictionary', 'hash', 'tree', 'graph',
        'stack', 'queue', 'recursion', 'iteration', 'loop', 'sort', 'search',
        'binary', 'api', 'async', 'promise', 'callback', 'object', 'class'
    }
}

# Task type indicators
TASK_KEYWORDS = {
    "general": {"what", "who", "when", "where", "tell", "describe"},
    "analysis": {"why", "how", "analyze", "explain", "compare"},
    "code": CODE_KEYWORDS,
    "qa": {"what is", "define", "meaning of", "difference between"}
}

class ModelService:
    """Service for managing and routing between different models."""
    
    def __init__(self):
        """Initialize the model service."""
        self._models = {}
        self._last_update = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self._device}")
        
    async def initialize(self):
        """Initialize the default TinyLlama model."""
        try:
            # Only initialize TinyLlama at startup
            logger.info("Loading TinyLlama model...")
            self._models["tinyllama"] = {
                "model": Llama(
                    model_path=TINYLLAMA_PATH,
                    n_ctx=2048,
                    n_threads=4
                )
            }
            self._last_update = datetime.now()
            logger.info("TinyLlama model loaded successfully")
        except Exception as e:
            logger.error(f"Error initializing TinyLlama: {str(e)}")
            raise
            
    async def _load_model(self, model_name: str) -> bool:
        """Load a model on-demand.
        
        Args:
            model_name: Name of the model to load
            
        Returns:
            bool: True if model loaded successfully or already loaded
            
        Raises:
            TimeoutError: If model loading takes too long
            RuntimeError: If model loading fails
        """
        try:
            if model_name in self._models:
                return True
                
            logger.info(f"Loading {model_name} model on-demand...")
            
            if model_name == "gpt2":
                try:
                    # Load GPT-2 with timeout
                    async with async_timeout(30):  # 30 second timeout
                        self._models["gpt2"] = {
                            "model": AutoModelForCausalLM.from_pretrained(GPT2_PATH).to(self._device),
                            "tokenizer": AutoTokenizer.from_pretrained(GPT2_PATH)
                        }
                except TimeoutError:
                    logger.error("Timeout loading GPT-2 model")
                    raise
            elif model_name == "codellama":
                codellama_path = os.path.join(MODELS_DIR, "codellama-7b.Q4_K_M.gguf")
                if not os.path.exists(codellama_path):
                    logger.error(f"CodeLlama model not found at {codellama_path}")
                    return False
                
                try:
                    # Load CodeLlama with timeout
                    async with async_timeout(60):  # 60 second timeout for first load
                        self._models["codellama"] = {
                            "model": Llama(
                                model_path=codellama_path,
                                n_ctx=4096,  # Larger context window
                                n_threads=4,
                                n_gpu_layers=35  # Use GPU for inference if available
                            )
                        }
                except TimeoutError:
                    logger.error("Timeout loading CodeLlama model")
                    raise
            else:
                logger.error(f"Unknown model: {model_name}")
                return False
                
            logger.info(f"{model_name} model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading {model_name}: {str(e)}")
            return False
    
    def _analyze_query(self, query: str) -> Dict[str, any]:
        """
        Analyze query characteristics.
        
        Args:
            query: User query
            
        Returns:
            Dict with query characteristics
        """
        query = query.lower()
        words = set(query.split())
        
        # Check for code-related keywords by category
        matches = {
            category: len(words & keywords)
            for category, keywords in CODE_KEYWORDS.items()
        }
        
        total_matches = sum(matches.values())
        code_score = total_matches / len(words) if words else 0
        
        # Consider it a code query if:
        # 1. Has any language-specific keywords, or
        # 2. Has multiple code-related keywords (>5% of words)
        is_code_query = matches['languages'] > 0 or code_score > 0.05
        
        # Check complexity
        is_complex = bool(words & COMPLEX_KEYWORDS) or len(words) > 20
        
        # Detect primary task type
        task_scores = {}
        for task, keywords in TASK_KEYWORDS.items():
            score = len([w for w in words if any(kw in w for kw in keywords)])
            task_scores[task] = score
        
        primary_task = max(task_scores.items(), key=lambda x: x[1])[0]
        
        # Special handling for code queries
        if is_code_query:
            primary_task = "code"
            is_complex = True
        
        return {
            "is_complex": is_complex,
            "is_code": is_code_query,
            "code_score": code_score,
            "task_type": primary_task,
            "task_scores": task_scores,
            "word_count": len(words)
        }
    
    def _get_carbon_tier(self, carbon: int) -> str:
        """
        Get carbon intensity tier.
        
        Args:
            carbon: Carbon intensity in gCO2/kWh
            
        Returns:
            Carbon tier (low, medium, high)
        """
        if carbon < CARBON_THRESHOLDS["low"]:
            return "low"
        elif carbon < CARBON_THRESHOLDS["medium"]:
            return "medium"
        else:
            return "high"
    
    async def select_model(self, query: str, carbon: int) -> str:
        """
        Select appropriate model based on query and carbon intensity.
        
        Args:
            query: User query
            carbon: Current carbon intensity (gCO2/kWh)
            
        Returns:
            Selected model name
        """
        # Analyze query
        analysis = self._analyze_query(query)
        carbon_tier = self._get_carbon_tier(carbon)
        
        # Log analysis for debugging
        logger.info(f"Query analysis: {analysis}")
        logger.info(f"Carbon tier: {carbon_tier}")
        
        # Always try to use CodeLlama for code queries unless carbon is very high
        if analysis["is_code"] and carbon_tier != "high":
            logger.info("Code query detected - attempting to use CodeLlama")
            success = await self._load_model("codellama")
            if success:
                return "codellama"
            logger.warning("Failed to load CodeLlama, falling back to TinyLlama")
        
        # Use best available model for complex queries if carbon allows
        if carbon_tier != "high" and analysis["is_complex"]:
            task_type = analysis["task_type"]
            
            # Try to find the best model for the task
            for model_name, info in MODEL_INFO.items():
                if task_type in info["capabilities"] and (model_name in self._models or await self._load_model(model_name)):
                    logger.info(f"Using {model_name} for {task_type} task")
                    return model_name
        
        # Default to TinyLlama
        logger.info("Using TinyLlama for general query")
        return "tinyllama"
    
    async def generate_response(
        self,
        model_name: str,
        query: str,
        max_length: Optional[int] = 512
    ) -> str:
        """
        Generate response using selected model.
        
        Args:
            model_name: Name of model to use
            query: User query
            max_length: Maximum response length
            
        Returns:
            Generated response
            
        Raises:
            ValueError: If model not loaded or failed to load
        """
        # First try to load the requested model
        if model_name not in self._models:
            success = await self._load_model(model_name)
            if not success:
                logger.error(f"Failed to load {model_name}")
                if model_name != "tinyllama":
                    # Try to fall back to TinyLlama
                    logger.info("Falling back to TinyLlama")
                    model_name = "tinyllama"
                    if not await self._load_model("tinyllama"):
                        raise RuntimeError("Failed to load both requested model and fallback model")
                else:
                    raise RuntimeError("Failed to load TinyLlama model")
                
        model_info = self._models[model_name]
        try:
            if model_name == "tinyllama":
                # Format query for chat
                prompt = f"USER: {query}\nASSISTANT:"
                
                # Generate response
                response = model_info["model"](
                    prompt,
                    max_tokens=max_length,
                    temperature=0.7,
                    top_p=0.95,
                    repeat_penalty=1.1
                )
                
                response_text = response["choices"][0]["text"].strip()
                
                # Add closing code block if needed
                if "```python" in prompt and "```" not in response_text:
                    response_text = response_text + "\n```"
                    
                return response_text
                
            elif model_name == "codellama":
                # Format query for code generation
                base_prompt = ""
                if "write" in query.lower() or "implement" in query.lower():
                    base_prompt = (
                        f"USER: Write code for the following task: {query}\n"
                        f"ASSISTANT: Here's the implementation:\n"
                    )
                elif "explain" in query.lower():
                    base_prompt = (
                        f"USER: Explain the following code or concept: {query}\n"
                        f"ASSISTANT: Let me explain:\n"
                    )
                elif "debug" in query.lower() or "fix" in query.lower():
                    base_prompt = (
                        f"USER: Help me debug/fix this code: {query}\n"
                        f"ASSISTANT: Let's analyze and fix the code.\n"
                        f"Here's the corrected version:\n"
                    )
                else:
                    base_prompt = f"USER: {query}\nASSISTANT: Let me help you with that.\n"
                
                # First get initial response
                response = model_info["model"](
                    base_prompt,
                    max_tokens=max_length // 2,  # Save tokens for potential code
                    temperature=0.7,
                    top_p=0.95,
                    repeat_penalty=1.1,
                    stop=["USER:", "```", "\n\n\n"]
                )
                
                initial_response = response["choices"][0]["text"].strip()
                
                # For code-related queries, get the code separately
                if "write" in query.lower() or "implement" in query.lower() or "debug" in query.lower() or "fix" in query.lower():
                    code_prompt = base_prompt + initial_response + "\n\nHere's the code:\n```python\n"
                    
                    code_response = model_info["model"](
                        code_prompt,
                        max_tokens=max_length // 2,
                        temperature=0.7,
                        top_p=0.95,
                        repeat_penalty=1.1,
                        stop=["USER:", "\n\n\n", "```"]
                    )
                    
                    code = code_response["choices"][0]["text"].strip()
                    
                    # Format final response with proper code block
                    response_text = f"{initial_response}\n\nHere's the code:\n```python\n{code}\n```"
                else:
                    response_text = initial_response
                    
                return response_text
                
            elif model_name == "gpt2":
                # Tokenize input
                model = model_info["model"]
                tokenizer = model_info["tokenizer"]
                
                # Format query
                prompt = f"Question: {query}\nAnswer:"
                inputs = tokenizer(prompt, return_tensors="pt").to(self._device)
                
                # Generate response
                with torch.no_grad():
                    outputs = model.generate(
                        inputs["input_ids"],
                        max_length=len(inputs["input_ids"][0]) + max_length,
                        num_return_sequences=1,
                        temperature=0.7,
                        top_p=0.95,
                        repetition_penalty=1.1,
                        pad_token_id=tokenizer.eos_token_id
                    )
                
                # Decode and clean response
                response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = response.replace(prompt, "").strip()
                
                return response
                
                # Generate response
                response = model(
                    prompt,
                    max_tokens=max_length,
                    temperature=0.7,
                    top_p=0.95,
                    repeat_penalty=1.1,
                    stop=["USER:", "\n"]
                )
                
                response_text = response["choices"][0]["text"].strip()
                
                # Add closing code block if needed
                if "```python" in prompt and "```" not in response_text:
                    response_text = response_text + "\n```"
                    
                return response_text
                
            else:
                raise ValueError(f"Unknown model type: {model_name}")
                
        except Exception as e:
            logger.error(f"Error generating response with {model_name}: {str(e)}")
            raise