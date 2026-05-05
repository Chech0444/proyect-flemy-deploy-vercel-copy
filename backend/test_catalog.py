import urllib.request
import json

url = "http://127.0.0.1:8042/api/v1/courses/catalog/"
try:
    print(f"Probando conexion a {url}...")
    with urllib.request.urlopen(url, timeout=5) as response:
        status = response.getcode()
        body = response.read().decode('utf-8')
        print(f"Status Code: {status}")
        print(f"Response: {json.dumps(json.loads(body), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
