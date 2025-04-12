import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_carbon_api():
    try:
        response = requests.get(
            "https://api.electricitymap.org/v3/carbon-intensity/latest",
            params={"zone": "IN-NO"},
            headers={
                "auth-token": "KnVGxwFL5wrrbWJeA4NO"
            }
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        logger.info(f"API Response: {data}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error accessing the API: {e}")
        return None

if __name__ == "__main__":
    test_carbon_api()
