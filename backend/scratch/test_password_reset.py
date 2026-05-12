import requests

url = "http://127.0.0.1:8000/api/v1/auth/password-reset/"
email = "santytiradol@gmail.com"

print(f"Probando recuperación de contraseña para: {email}")
try:
    response = requests.post(url, json={"email": email})
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")
except Exception as e:
    print(f"Error al conectar con la API: {e}")
