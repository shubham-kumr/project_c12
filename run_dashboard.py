"""
Script to run the Streamlit dashboard.
"""

import os
import sys
import subprocess
import traceback
from typing import Optional

def setup_python_path() -> Optional[str]:
    """
    Set up the Python path and return the project root.
    
    Returns:
        Project root directory or None if setup fails
    """
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.abspath(__file__))
        
        # Add the project root to the Python path
        sys.path.insert(0, project_root)
        
        # Verify the import path
        try:
            import src
            import src.dashboard
        except ImportError as e:
            print(f"Error: Could not import required packages: {e}")
            print("Please make sure you have installed the project in development mode:")
            print("pip install -e .")
            return None
            
        return project_root
    except Exception as e:
        print(f"Error setting up Python path: {e}")
        traceback.print_exc()
        return None

def run_dashboard(project_root: str) -> bool:
    """
    Run the Streamlit dashboard.
    
    Args:
        project_root: Path to the project root directory
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Import the dashboard app
        from src.dashboard.app import main as dashboard_main
        
        # Run the dashboard
        dashboard_main()
        return True
    except ImportError as e:
        print(f"Error importing dashboard: {e}")
        print("Please check that all required packages are installed:")
        print("pip install -r requirements-dashboard.txt")
        return False
    except Exception as e:
        print(f"Error running dashboard: {e}")
        traceback.print_exc()
        return False

def main():
    """Run the Streamlit dashboard with error handling."""
    # Set up Python path
    project_root = setup_python_path()
    if not project_root:
        sys.exit(1)
    
    # Run the dashboard
    if not run_dashboard(project_root):
        sys.exit(1)

if __name__ == "__main__":
    main() 