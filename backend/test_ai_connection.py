import os
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI

# Cargar variables
load_dotenv()
google_key = os.getenv("GOOGLE_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

print("--- Probando OpenAI ---")
client = OpenAI(api_key=openai_key)
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Dime 'OK'"}],
        max_tokens=5
    )
    print(f"Respuesta OpenAI: {response.choices[0].message.content}")
except Exception as e:
    print(f"Error OpenAI: {str(e)}")

print("\n--- Probando Google Gemini ---")
genai.configure(api_key=google_key)
model = genai.GenerativeModel('gemini-2.5-flash-preview')
try:
    response = model.generate_content("Dime 'OK'")
    print(f"Respuesta Gemini: {response.text}")
except Exception as e:
    print(f"Error Gemini: {str(e)}")
