"""
Servicio de IA para herramientas interactivas (Chatbot, Code Feedback, etc).

Usa Google Gemini (gemini-3-flash-preview) para:
- Chatbot contextual basado en la transcripción del video de cada lección
- Feedback de código en tiempo real
- Generación de ejercicios

Reutiliza la misma GEMINI_API_KEY y modelo que el servicio principal de IA.
"""

import logging

import google.generativeai as genai
from django.conf import settings

from courses.models import Lesson

logger = logging.getLogger(__name__)

# ─── Inicialización del modelo Gemini ───
_model = None


def _get_model():
    """Obtiene la instancia del modelo Gemini, inicializándola si es necesario."""
    global _model
    if _model is not None:
        return _model

    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        logger.warning('GEMINI_API_KEY no configurada para ai_tools.')
        return None

    try:
        genai.configure(api_key=api_key)
        _model = genai.GenerativeModel('gemini-3-flash-preview')
        logger.info('Gemini API (ai_tools) inicializada correctamente.')
        return _model
    except Exception as e:
        logger.error(f'Error al inicializar Gemini para ai_tools: {e}')
        return None


def _get_lesson_context(lesson: Lesson) -> str:
    """
    Construye el contexto de la lección para la IA.
    Prioriza la transcripción del video (si existe), luego el contenido de la lección.
    """
    context_parts = [f"Título de la lección: {lesson.title}"]

    # Contenido escrito de la lección
    if lesson.content:
        context_parts.append(f"Contenido de la lección:\n{lesson.content}")

    # Transcripción del video (la fuente de contexto más rica)
    try:
        if hasattr(lesson, 'video') and hasattr(lesson.video, 'transcription'):
            transcription = lesson.video.transcription
            if transcription and transcription.full_text:
                # Limitar a ~4000 chars para no exceder tokens
                text = transcription.full_text[:4000]
                context_parts.append(f"Transcripción del video:\n{text}")
    except Exception:
        pass

    # Resumen generado por IA (si existe)
    try:
        if hasattr(lesson, 'video') and hasattr(lesson.video, 'summary'):
            summary = lesson.video.summary
            if summary and summary.content:
                context_parts.append(f"Resumen del video:\n{summary.content}")
    except Exception:
        pass

    return "\n\n".join(context_parts)


def generate_transcription_text(lesson: Lesson) -> str:
    """Genera texto de transcripción para una lección."""
    try:
        if hasattr(lesson, 'video') and hasattr(lesson.video, 'transcription'):
            return lesson.video.transcription.full_text or "No hay transcripción disponible."
    except Exception:
        pass
    return "No hay transcripción disponible para esta lección."


def generate_exercise_payload(lesson: Lesson):
    """Genera ejercicios de práctica basados en el contenido de la lección."""
    model = _get_model()
    if not model:
        return [{"error": "GEMINI_API_KEY no configurada"}]

    context = _get_lesson_context(lesson)
    prompt = f"""Basado en el siguiente contenido educativo, genera exactamente 3 ejercicios de práctica.
Responde SOLO con un JSON válido: una lista de objetos, cada uno con "question" y "hint".

Contenido:
{context[:3000]}"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f'Error generando ejercicios: {e}')
        return [{"error": str(e)}]


def generate_code_feedback(language: str, code: str) -> str:
    """Analiza el código del estudiante y da feedback como tutor."""
    model = _get_model()
    if not model:
        return "[ERROR]: GEMINI_API_KEY no configurada"

    prompt = f"""Actúa como una consola inteligente de tutoría. Analiza este código en {language}:

```{language}
{code}
```

Tu respuesta debe ser breve (máximo 3 frases) y seguir este formato:
1. Comienza con [ESTADO]: OK o MAL (si hay errores de sintaxis o lógica).
2. Da una pista directa sobre cómo mejorar o qué falló.
3. Una frase de motivación corta."""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f'Error generando feedback: {e}')
        return f"[ERROR DEL SISTEMA]: {str(e)}"


def generate_chatbot_answer(lesson: Lesson, question: str) -> str:
    """
    Asistente interactivo contextual.
    Usa la transcripción del video + contenido de la lección como contexto
    para responder preguntas del estudiante.
    """
    model = _get_model()
    if not model:
        return "Error: El servicio de IA no está disponible en este momento."

    context = _get_lesson_context(lesson)

    prompt = f"""Eres "Flemy AI", un tutor educativo amigable y experto.
Tienes acceso al contenido de la lección que el estudiante está viendo.

CONTEXTO DE LA LECCIÓN:
{context}

PREGUNTA DEL ESTUDIANTE:
{question}

INSTRUCCIONES:
- Responde de forma clara, concisa y amigable.
- Basa tu respuesta en el contexto de la lección proporcionado.
- Si la pregunta no tiene relación con el tema, redirígelo amablemente al contenido.
- Usa ejemplos simples cuando sea útil.
- Responde en español.
- Máximo 150 palabras."""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f'Error en chatbot: {e}')
        return "Lo siento, no pude procesar tu pregunta en este momento. Inténtalo de nuevo en unos segundos."
