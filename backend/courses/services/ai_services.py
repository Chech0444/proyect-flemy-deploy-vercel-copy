"""
Servicio de Inteligencia Artificial.

Usa la API de Google Gemini (GRATIS) para:
- Generar resúmenes estructurados de transcripciones
- Generar preguntas tipo quiz con opciones múltiples
"""

import json
import logging
import re

from django.conf import settings

logger = logging.getLogger(__name__)


class AIService:
    """
    Servicio de IA usando Google Gemini API (tier gratuito).
    Genera resúmenes y preguntas de quiz a partir de
    transcripciones de video.
    """

    def __init__(self):
        self._model = None
        self._is_configured = False

    def _initialize(self):
        """Inicializa el cliente de Google Gemini."""
        if self._model is not None:
            return

        api_key = getattr(settings, 'GEMINI_API_KEY', '')
        if not api_key:
            logger.warning(
                'GEMINI_API_KEY no está configurada. '
                'La IA usará el modo fallback (simulado). '
                'Obtén tu API key gratis en: https://aistudio.google.com/apikey'
            )
            self._is_configured = False
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel('gemini-2.0-flash')
            self._is_configured = True
            logger.info('Google Gemini API inicializada correctamente')
        except Exception as e:
            logger.error(f'Error al inicializar Gemini API: {e}')
            self._is_configured = False

    def _parse_json_response(self, text: str) -> dict | list:
        """
        Extrae JSON de la respuesta de Gemini.
        Gemini a veces envuelve el JSON en bloques de código markdown.
        """
        # Intentar parsear directamente
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Buscar JSON dentro de bloques de código markdown
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Buscar cualquier JSON en el texto
        json_match = re.search(r'[\[{].*[\]}]', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        raise ValueError(f'No se pudo extraer JSON de la respuesta: {text[:200]}')

    def generate_educational_content(self, transcription_text: str, num_questions: int = 5) -> dict:
        """
        Genera simultáneamente el resumen y las preguntas del quiz
        usando UNA SOLA llamada a la API de Gemini para ahorrar tokens y peticiones.
        """
        self._initialize()
        num_questions = max(num_questions, 5)

        if not self._is_configured:
            return {
                'summary': self._fallback_summary(transcription_text),
                'quiz': self._fallback_quiz(transcription_text, num_questions)
            }

        try:
            prompt = f"""Eres un catedrático universitario y pedagogo experto.
Analiza la siguiente transcripción de un video educativo y genera un JSON estructurado que contenga DOS partes: un resumen detallado y un quiz de evaluación.
IMPORTANTE: El usuario final acaba de ver un VIDEO. Por lo tanto, tu respuesta debe parecer que estás analizando un video directamente. NUNCA menciones palabras como "texto", "transcripción", "documento" o "lectura".

TRANSCRIPCIÓN:
---
{transcription_text[:12000]}
---

Responde ÚNICAMENTE con un objeto JSON válido (sin bloques de código markdown, sin texto adicional) con esta estructura exacta:
{{
    "summary": {{
        "content": "Un resumen exhaustivo y fluido. Inicia siempre haciendo referencia al video (ej. 'En este video se explica...', 'Según el video mostrado...'). Redacta entre 4 y 7 párrafos nutridos, lenguaje profesional.",
        "key_points": [
            "Concepto Clave 1: Explicación profunda.",
            "Concepto Clave 2: Explicación detallada."
        ]
    }},
    "quiz": [
        {{
            "question": "Pregunta compleja que evalúe pensamiento crítico. Debe estar formulada refiriéndose al video (ej. 'Según el video, ¿qué...?', 'En el video se menciona que...').",
            "options": [
                "Opción A estructurada e inteligente (distractor)",
                "Opción B argumentada (distractor)",
                "Opción C (respuesta verdadera, clara e indiscutible)",
                "Opción D (distractor tramposo)"
            ],
            "correct_option": 2,
            "explanation": "Explicación didáctica basada en lo mostrado en el video."
        }}
    ]
}}

Reglas del Quiz:
- Crea EXACTAMENTE {num_questions} preguntas.
- Cada pregunta debe tener exactamente 4 opciones.
- "correct_option" debe ser un entero (0, 1, 2, o 3).
- Altera aleatoriamente la ubicación de las respuestas correctas.
- RECUERDA: Tanto el resumen como las preguntas y explicaciones deben hablar explícitamente del "video".
Todo el contenido generado debe estar en el mismo idioma predominante de la transcripción original."""

            response = self._model.generate_content(prompt)
            result = self._parse_json_response(response.text)

            # Validar y extraer Summary
            summary_data = result.get('summary', {})
            if not isinstance(summary_data, dict):
                summary_data = {}

            # Validar y extraer Quiz
            quiz_raw = result.get('quiz', [])
            quiz_questions = []
            if isinstance(quiz_raw, list):
                for q in quiz_raw:
                    if all(k in q for k in ['question', 'options', 'correct_option']):
                        quiz_questions.append({
                            'question': q['question'],
                            'options': q['options'][:4],
                            'correct_option': min(q['correct_option'], 3),
                            'explanation': q.get('explanation', '')
                        })

            logger.info('Resumen y Quiz generados exitosamente en una sola petición con Gemini')
            return {
                'summary': {
                    'content': summary_data.get('content', 'Resumen no generado adecuadamente.'),
                    'key_points': summary_data.get('key_points', [])
                },
                'quiz': quiz_questions
            }

        except Exception as e:
            logger.error(f'Error al generar contenido con Gemini: {e}')
            logger.info('Usando modo fallback para el contenido')
            return {
                'summary': self._fallback_summary(transcription_text),
                'quiz': self._fallback_quiz(transcription_text, num_questions)
            }

    def generate_summary_only(self, transcription_text: str) -> dict:
        self._initialize()
        if not self._is_configured:
            return self._fallback_summary(transcription_text)

        try:
            prompt = f"""Eres un catedrático universitario y pedagogo experto.
Analiza la siguiente transcripción de un video educativo y genera SOLO un JSON con el resumen.
IMPORTANTE: El usuario final acaba de ver un VIDEO. NUNCA menciones palabras como "texto", "transcripción" o "documento".

TRANSCRIPCIÓN:
---
{transcription_text[:12000]}
---

Responde ÚNICAMENTE con un objeto JSON válido con esta estructura exacta:
{{
    "content": "Un resumen exhaustivo y fluido. Inicia siempre haciendo referencia al video (ej. 'En este video se explica...'). Redacta entre 4 y 7 párrafos nutridos.",
    "key_points": [
        "Concepto Clave 1",
        "Concepto Clave 2"
    ]
}}"""
            response = self._model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            return {
                'content': result.get('content', 'Resumen no generado adecuadamente.'),
                'key_points': result.get('key_points', [])
            }
        except Exception as e:
            logger.error(f'Error al generar solo resumen: {e}')
            return self._fallback_summary(transcription_text)

    def generate_quiz_only(self, transcription_text: str, num_questions: int = 8) -> list:
        self._initialize()
        if not self._is_configured:
            return self._fallback_quiz(transcription_text, num_questions)

        try:
            prompt = f"""Eres un catedrático universitario y pedagogo experto.
Analiza la siguiente transcripción de un video educativo y genera SOLO un JSON con preguntas de quiz.
IMPORTANTE: El usuario final acaba de ver un VIDEO. Las preguntas deben referirse al video. NUNCA menciones "texto" o "transcripción".

TRANSCRIPCIÓN:
---
{transcription_text[:12000]}
---

Responde ÚNICAMENTE con una lista JSON válida con {num_questions} preguntas, cada una con esta estructura exacta:
[
    {{
        "question": "Pregunta referida al video.",
        "options": ["Opcion A", "Opcion B", "Opcion C", "Opcion D"],
        "correct_option": 2,
        "explanation": "Explicación basada en el video."
    }}
]"""
            response = self._model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            quiz_questions = []
            if isinstance(result, list):
                for q in result:
                    if all(k in q for k in ['question', 'options', 'correct_option']):
                        quiz_questions.append({
                            'question': q['question'],
                            'options': q['options'][:4],
                            'correct_option': min(q['correct_option'], 3),
                            'explanation': q.get('explanation', '')
                        })
            return quiz_questions
        except Exception as e:
            logger.error(f'Error al generar solo quiz: {e}')
            return self._fallback_quiz(transcription_text, num_questions)

    # ===================================================
    # Métodos de fallback (cuando no hay API key)
    # ===================================================

    def _fallback_summary(self, transcription_text: str) -> dict:
        """Genera un resumen básico sin IA como fallback."""
        sentences = transcription_text.replace('...', '.').split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        summary_sentences = sentences[:min(8, len(sentences))]
        content = '. '.join(summary_sentences) + '.'

        sorted_sentences = sorted(sentences, key=len, reverse=True)
        key_points = [s.strip() + '.' for s in sorted_sentences[:5]]

        return {
            'content': content,
            'key_points': key_points
        }

    def _fallback_quiz(self, transcription_text: str, num_questions: int) -> list:
        """Genera preguntas básicas sin IA como fallback."""
        sentences = transcription_text.replace('...', '.').split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

        questions = []
        for i in range(min(num_questions, len(sentences))):
            sentence = sentences[i]
            words = sentence.split()
            if len(words) < 5:
                continue

            questions.append({
                'question': f'Según el contenido del video, ¿qué se menciona sobre: "{" ".join(words[:6])}..."?',
                'options': [
                    sentence[:80] + '...' if len(sentence) > 80 else sentence,
                    'Esta información no se menciona en el video',
                    'El video trata sobre un tema completamente diferente',
                    'Ninguna de las anteriores es correcta'
                ],
                'correct_option': 0,
                'explanation': f'La respuesta se encuentra directamente en la transcripción del video.'
            })

        while len(questions) < num_questions:
            questions.append({
                'question': f'Pregunta {len(questions) + 1}: ¿Cuál es uno de los temas tratados en este video?',
                'options': [
                    'El contenido principal del video',
                    'Un tema no relacionado con el video',
                    'Información contradictoria al video',
                    'Datos que no aparecen en el video'
                ],
                'correct_option': 0,
                'explanation': 'Esta pregunta fue generada automáticamente como respaldo.'
            })

        return questions[:num_questions]


# Instancia singleton del servicio
ai_service = AIService()
