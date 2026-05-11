import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc3ODUwMjMyLCJpYXQiOjE3Nzc4NDY2MzIsImp0aSI6IjkxODY3ZGEyNmNlMDQ1MzBhYjM2YjllZTY4MjdkZTQ5IiwidXNlcl9pZCI6IjEifQ.hBBQ56nxo45MvntADHBkOhAYTAlCnaduIaSUCqQ1D10"
url = "http://localhost:8042/api/v1/auth/profile/"
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
