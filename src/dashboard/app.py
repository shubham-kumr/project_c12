"""
Main Streamlit dashboard application for Project-C12 Carbon-Aware Model Router.
"""

import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="Project-C12",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

import requests
from datetime import datetime
import logging
import os
from typing import Dict, Optional
from src.dashboard.services.db import DatabaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================
#  Configuration
# ======================
API_BASE = "http://localhost:8000"  # Base API URL
API_HEALTH = f"{API_BASE}/api/health"  # Health check endpoint
API_CARBON = f"{API_BASE}/api/carbon-intensity"  # Carbon data endpoint
API_QUERY = f"{API_BASE}/api/ask"  # Query endpoint

# Initialize database
db = DatabaseService()

# Model energy consumption (kWh per 1k tokens)
MODEL_ENERGY = {
    "tinyllama": 0.001,  # TinyLlama is very efficient
    "gpt2": 0.01,      # Medium model for comparison
    "gpt4": 0.1        # Large model for comparison
}

# Custom CSS with IBM Plex Mono font
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap');

/* Apply IBM Plex Mono to all text */
.stMarkdown, .stText, .stTitle, .stHeader, .stSubheader, .stTextInput, .stButton, .stMetric {
    font-family: 'IBM Plex Mono', monospace !important;
}

/* Status indicators */
.status-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}

.status-online {
    background-color: #00ff00;
}

.status-offline {
    background-color: #ff0000;
}

.status-text {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 14px;
}

/* Metrics styling */
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600;
}

[data-testid="stMetricLabel"] {
    font-family: 'IBM Plex Mono', monospace !important;
}

/* Input and button styling */
.stTextInput input {
    font-family: 'IBM Plex Mono', monospace !important;
}

.stButton button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 500;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600;
}

/* Code blocks */
code {
    font-family: 'IBM Plex Mono', monospace !important;
}

/* Dark theme overrides */
.stApp {
    background-color: #0E1117;
    color: #E0E0E0;
}

.stSidebar {
    background-color: #1A1F25;
}

.stButton button {
    background-color: #2E3640;
    border: 1px solid #4A5568;
    color: #E0E0E0;
}

.stTextInput input {
    background-color: #1A1F25;
    border: 1px solid #4A5568;
    color: #E0E0E0;
}

.stMetric {
    background-color: #1A1F25;
    border-radius: 4px;
    padding: 8px;
}
</style>
""", unsafe_allow_html=True)

# ======================
#  Helper Functions
# ======================
def check_api_status() -> bool:
    """Check if API is available."""
    try:
        response = requests.get(API_HEALTH, timeout=5)
        return response.ok
    except requests.Timeout:
        logger.warning("API health check timed out")
        return False
    except requests.ConnectionError:
        logger.warning("Could not connect to API")
        return False
    except Exception as e:
        logger.error(f"Error checking API status: {str(e)}")
        return False

def get_carbon_data() -> Dict:
    """Get carbon intensity data."""
    try:
        response = requests.get(API_CARBON, timeout=2)
        if response.ok:
            return response.json()
        return {}
    except:
        return {}

def calculate_savings(query_length: int, carbon_intensity: float) -> float:
    """
    Estimate CO2 savings compared to baseline model.
    
    Args:
        query_length: Length of the query in characters
        carbon_intensity: Current carbon intensity in gCO2/kWh
        
    Returns:
        Estimated CO2 savings in grams
    """
    # Convert character length to approximate token count (4 chars per token)
    tokens = query_length / 4
    
    # Calculate energy usage in kWh
    tinyllama_energy = MODEL_ENERGY["tinyllama"] * tokens / 1000
    gpt2_energy = MODEL_ENERGY["gpt2"] * tokens / 1000
    
    # Calculate emissions in gCO2
    savings = (gpt2_energy - tinyllama_energy) * carbon_intensity
    return max(0.0, savings)  # Ensure non-negative

def format_model_name(model_name: str) -> str:
    """Format model name for display."""
    return model_name.upper() if model_name else "Unknown"

# Initialize session state
if 'api_status' not in st.session_state:
    st.session_state.api_status = False
if 'carbon_status' not in st.session_state:
    st.session_state.carbon_status = False
if 'carbon_intensity' not in st.session_state:
    st.session_state.carbon_intensity = 0
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = 'auto'
if 'is_code_query' not in st.session_state:
    st.session_state.is_code_query = False
if 'recommended_model' not in st.session_state:
    st.session_state.recommended_model = 'tinyllama'

# Load metrics from database
metrics = db.get_metrics()
if 'co2_saved' not in st.session_state:
    st.session_state.co2_saved = metrics['co2_saved']
if 'queries_optimized' not in st.session_state:
    st.session_state.queries_optimized = metrics['queries_optimized']

# Update status every 10 seconds
if 'last_update' not in st.session_state or \
   (datetime.now() - st.session_state.last_update).total_seconds() > 10:
    st.session_state.api_status = check_api_status()
    carbon_data = get_carbon_data()
    st.session_state.carbon_status = bool(carbon_data)
    st.session_state.carbon_intensity = carbon_data.get('carbon_intensity', 0)
    st.session_state.last_update = datetime.now()

# Sidebar
with st.sidebar:
    st.title("Project_C12")
    st.subheader("Toward Sustainable AI with Carbon-Aware Interface")
    
    st.markdown("### System Status")
    
    # API Connection
    st.markdown(
        f"API Connection: <span class='status-indicator status-{'online' if st.session_state.api_status else 'offline'}'></span>"
        f"<span class='status-text'>{'Online' if st.session_state.api_status else 'Offline'}</span>",
        unsafe_allow_html=True
    )
    
    # Carbon Data Status
    st.markdown(
        f"Carbon Data Status: <span class='status-indicator status-{'online' if st.session_state.carbon_status else 'offline'}'></span>"
        f"<span class='status-text'>{'Online' if st.session_state.carbon_status else 'Offline'}</span>",
        unsafe_allow_html=True
    )
    
    # Current Carbon Intensity
    if st.session_state.carbon_status:
        st.markdown(f"Carbon Intensity: **{st.session_state.carbon_intensity:.0f} gCO2/kWh**")
    
    # Last Update
    st.markdown(f"Last Update: {st.session_state.last_update.strftime('%H:%M:%S')}")
    
    # CO2 Savings
    st.markdown("### Carbon Impact")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "CO2 Saved",
            f"{st.session_state.co2_saved:.1f}g",
            help="Total CO2 emissions saved by using smaller models when possible"
        )
    with col2:
        st.metric(
            "Queries Optimized",
            st.session_state.queries_optimized,
            help="Number of queries that used a more efficient model"
        )

# Main content
st.markdown("### Ask me anything:")

# Model selection
col1, col2 = st.columns([2, 1])
with col1:
    model_options = ['auto', 'tinyllama', 'codellama', 'gpt2']
    selected_model = st.selectbox(
        "Select Model",
        model_options,
        index=model_options.index(st.session_state.selected_model),
        help="'auto' will choose the best model based on query type and carbon intensity"
    )
    st.session_state.selected_model = selected_model

with col2:
    eco_mode = st.toggle("Eco Mode", value=True, help="Prioritize energy-efficient models when carbon intensity is high")

# Query input with real-time analysis
def on_query_change():
    query = st.session_state.query_input
    # Check for code-related keywords
    code_keywords = ['code', 'function', 'class', 'programming', 'algorithm', 'implement', 
                    'debug', 'error', 'python', 'javascript', 'java', 'c++', 'html', 'css']
    st.session_state.is_code_query = any(keyword in query.lower() for keyword in code_keywords)
    
    # Update model selection if in auto mode
    if st.session_state.selected_model == 'auto' and st.session_state.is_code_query:
        st.session_state.recommended_model = 'codellama'
    elif st.session_state.selected_model == 'auto':
        st.session_state.recommended_model = 'tinyllama'

query = st.text_input(
    "Type your question here...",
    key="query_input",
    on_change=on_query_change
)

# Show real-time analysis
if query:
    if st.session_state.is_code_query:
        st.caption("📝 This appears to be a code-related query. CodeLlama is recommended.")
    if st.session_state.selected_model == 'auto':
        st.caption(f"🤖 Auto-selecting: {st.session_state.recommended_model}")

if st.button("Get Answer", key="submit_button"):
    if not st.session_state.api_status:
        st.error("API is currently offline. Please try again later.")
    elif query:
        try:
            start_time = datetime.now()
            
            # Determine which model to use
            model_to_use = st.session_state.selected_model
            if model_to_use == 'auto':
                model_to_use = st.session_state.recommended_model
            
            # Show loading message
            with st.status("Generating response...", expanded=True) as status:
                status.write(f"Using model: {model_to_use}")
                    
                try:
                    # First try with shorter timeout
                    response = requests.post(
                        API_QUERY,
                        json={
                            "text": query,
                            "max_length": 512,
                            "model": model_to_use
                        },
                        timeout=60  # Initial timeout
                    )
                except requests.Timeout:
                    # If it times out, show message and retry with longer timeout
                    status.write("Initial attempt timed out. Retrying with longer timeout...")
                    response = requests.post(
                        API_QUERY,
                        json={
                            "text": query,
                            "max_length": 512,
                            "model": model_to_use
                        },
                        timeout=120  # Extended timeout
                    )
                
                # Calculate processing time
                processing_time = (datetime.now() - start_time).total_seconds()
                status.write(f"Response generated in {processing_time:.1f} seconds")
            
            response.raise_for_status()  # Raise error for bad status
            data = response.json()
            
            # Validate required fields
            if "response" not in data:
                raise ValueError("API response missing 'response' field")
            if "carbon_intensity" not in data:
                raise ValueError("API response missing 'carbon_intensity' field")
            if "model" not in data:
                raise ValueError("API response missing 'model' field")
            
            # Display response and metrics in a clean layout
            st.markdown("### Response")
            
            # Display response with proper formatting
            response_text = data["response"]
            
            # Split by code blocks if present
            if "```" in response_text:
                # Split by code blocks
                parts = response_text.split("```")
                
                # Display each part appropriately
                for i, part in enumerate(parts):
                    if i % 2 == 0:  # Non-code part
                        if part.strip():
                            st.write(part.strip())
                    else:  # Code part
                        # Extract language if specified
                        code_lines = part.strip().split('\n')
                        if code_lines[0] in ['python', 'javascript', 'java', 'cpp', 'c++', 'c']:
                            language = code_lines[0]
                            code = '\n'.join(code_lines[1:])
                        else:
                            language = 'python'  # Default to Python
                            code = part.strip()
                            
                        # Display code with copy button
                        st.code(code, language=language, line_numbers=True)
            else:
                # Regular response
                st.info(response_text)
            
            # Metrics in a nice grid
            st.markdown("### Performance Metrics")
            col1, col2, col3 = st.columns(3)
                
            with col1:
                model_display = data["model"].title()
                st.metric(
                    "Model Used",
                    model_display,
                    help={
                        "tinyllama": "Efficient small language model",
                        "codellama": "Specialized code model",
                        "gpt2": "Medium-sized general model"
                    }.get(data["model"], "Unknown model")
                )
            with col2:
                st.metric(
                    "Carbon Intensity",
                    f"{data['carbon_intensity']:.0f} gCO2/kWh",
                    help="Current carbon intensity from Electricity Map"
                )
            with col3:
                # Calculate CO2 savings
                savings = calculate_savings(
                    query_length=len(query),
                    carbon_intensity=data["carbon_intensity"]
                )
                
                if savings > 0:
                    # Update database
                    db.add_savings(savings, query_optimized=True)
                    
                    # Update session state
                    st.session_state.co2_saved += savings
                    if eco_mode:
                        st.session_state.queries_optimized += 1
                    
                st.metric(
                    "CO2 Savings",
                    f"{savings:.2f}g",
                    help="Estimated CO2 savings compared to using GPT-2"
                )
                
                # Display processing time if available
                if "processing_time" in data:
                    st.caption(
                        f"Processing time: {data['processing_time']:.2f} seconds"
                    )
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the API. Please check if the service is running.")
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {str(e)}")
        except ValueError as e:
            st.error(f"Data Error: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected Error: {str(e)}")
    else:
        st.warning("Please enter a question")