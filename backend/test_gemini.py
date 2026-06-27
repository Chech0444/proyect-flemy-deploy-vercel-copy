import os
import sys
from dotenv import load_dotenv

# Cargar .env manualmente para asegurar que toma la última llave
load_dotenv(override=True)

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
import google.generativeai as genai

def test_gemini():
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        print("❌ ERROR: No se encontró la GEMINI_API_KEY en el archivo .env")
        return
        
    print(f"Probando llave: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-preview')
        print("Enviando petición de prueba a Google Gemini...")
        response = model.generate_content("Responde únicamente con la palabra: VERDE")
        
        if "VERDE" in response.text.strip().upper():
            print("\n✅ VERDE! Conexión exitosa con Gemini.")
        else:
            print(f"\n⚠️ Conexión exitosa, pero respuesta inesperada: {response.text}")
            
    except Exception as e:
        print("\n❌ ERROR AL CONECTAR CON GEMINI:")
        print(str(e))

if __name__ == "__main__":
    test_gemini()
