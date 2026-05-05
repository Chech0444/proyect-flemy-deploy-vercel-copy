import requests

url = "http://localhost:8042/api/v1/auth/login/"
payload = {"username": "admin", "password": "admin123"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
