import os
from google import genai   
from openai import OpenAI
from courses.models import Lesson



# Configuración Inicial con la nueva librería google-genai
# La API KEY se toma de la variable de entorno GOOGLE_API_KEY
client_gemini = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
client_openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_transcription_text(lesson: Lesson) -> str:
    """
    Utiliza OpenAI Whisper para transcribir el video de la lección.
    """
    if not lesson.video_url:
        return "No hay URL de video disponible."
    
    try:
        # En una implementación real, aquí descargaríamos el audio y lo enviaríamos a Whisper
        return f"Transcripción generada por Whisper para: {lesson.title}. [Pendiente descarga de audio]"
    except Exception as e:
        return f"Error en transcripción: {str(e)}"

def generate_exercise_payload(lesson: Lesson):
    """
    Utiliza Gemini 2.0 Flash para crear ejercicios basados en el contenido.
    """
    prompt = f"""
    Basado en el siguiente contenido de una lección, genera 3 ejercicios de práctica 
    con una pregunta y una pista cada uno. Formato JSON lista de objetos.
    Contenido: {lesson.content or lesson.title}
    """
    
    try:
        response = client_gemini.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return [{"error": str(e)}]

def generate_code_feedback(language: str, code: str) -> str:
    """
    Analiza el código del estudiante y actúa como un tutor en la consola.
    """
    prompt = f"""
    Actúa como una consola inteligente de tutoría. Analiza este código en {language}:
    
    {code}
    
    Tu respuesta debe ser breve (máximo 3 frases) y seguir este formato:
    1. Comienza con [ESTADO]: OK o MAL (si hay errores de sintaxis o lógica).
    2. Da una pista directa sobre cómo mejorar o qué falló.
    3. Una frase de motivación corta.
    """
    
    try:
        response = client_gemini.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"[ERROR DEL SISTEMA]: {str(e)}"

def generate_chatbot_answer(lesson: Lesson, question: str) -> str:
    """
    Asistente interactivo basado en el contexto de la lección.
    """
    context = lesson.content or lesson.title
    prompt = f"Eres un tutor experto. Basado en esta lección: {context}. Responde a la pregunta del alumno: {question}"
    
    try:
        response = client_gemini.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error en el chatbot: {str(e)}"
