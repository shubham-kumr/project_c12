import requests

response = requests.get(
    "https://api.electricitymap.org/v3/carbon-intensity/latest?zone=IN-NO",
    headers={
        "auth-token": "KnVGxwFL5wrrbWJeA4NO"
    }
)
print(response.json())
