"""
Servicio de Inteligencia Artificial.

Usa la API de Google Gemini (GRATIS) para:
- Generar resúmenes estructurados de transcripciones
- Generar preguntas tipo quiz con opciones múltiples
"""

import json
import logging
import random
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
            self._model = genai.GenerativeModel('gemini-flash-latest')
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

    def _get_transcription_text(self, lesson_or_text) -> str:
        if isinstance(lesson_or_text, str):
            return lesson_or_text
        try:
            if hasattr(lesson_or_text, 'video') and lesson_or_text.video:
                if hasattr(lesson_or_text.video, 'transcription') and lesson_or_text.video.transcription:
                    return lesson_or_text.video.transcription.full_text or ''
            if lesson_or_text.content:
                return lesson_or_text.content
        except Exception:
            pass
        return ''

    def _shuffle_and_track_correct(self, options: list[str], correct_idx: int) -> tuple[list[str], int]:
        tagged = []
        for i, opt in enumerate(options):
            tagged.append((opt, i == correct_idx))
        random.shuffle(tagged)
        new_options = []
        new_correct = None
        for i, (text, is_correct) in enumerate(tagged):
            new_options.append(text)
            if is_correct:
                new_correct = i
        return new_options, new_correct if new_correct is not None else 0

    def _resolve_correct_option(self, options: list[str], explanation: str, ai_correct: int) -> int:
        # Priority 1: marker tag in option text
        for i, opt in enumerate(options):
            if '<<<CORRECTO>>>' in opt:
                return i

        # Priority 2: match explanation quotes against options
        if explanation:
            import re as _re
            quotes = _re.findall(r"'([^']+)'|\"([^\"]+)\"", explanation)
            for quote_tuple in quotes:
                quote = quote_tuple[0] or quote_tuple[1]
                if quote:
                    for i, opt in enumerate(options):
                        clean = opt.replace('<<<CORRECTO>>>', '').strip()
                        if quote.lower() in clean.lower() or clean.lower() in quote.lower():
                            return i
                        if len(quote) > 20 and (quote[:40].lower() in clean.lower() or clean[:40].lower() in quote.lower()):
                            return i

        # Priority 3: AI's correct_option (as fallback)
        if 0 <= ai_correct <= 3:
            return ai_correct
        return 0

    def _extract_quiz_questions(self, quiz_raw: list) -> list:
        questions = []
        for q in quiz_raw:
            if not all(k in q for k in ['question', 'options']):
                continue
            options = q['options'][:4]
            ai_correct = q.get('correct_option', 0)
            explanation = q.get('explanation', '')

            correct_option = self._resolve_correct_option(options, explanation, ai_correct)

            cleaned = []
            for opt in options:
                cleaned.append(opt.replace('<<<CORRECTO>>>', '').strip())
            options = cleaned

            options, correct_option = self._shuffle_and_track_correct(options, correct_option)

            questions.append({
                'question': q['question'],
                'options': options,
                'correct_option': correct_option,
                'explanation': explanation
            })
        return questions

    def generate_educational_content(self, lesson_or_text, num_questions: int = 5) -> dict:
        self._initialize()
        num_questions = max(num_questions, 5)
        transcription_text = self._get_transcription_text(lesson_or_text)

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
            "question": "Pregunta compleja que evalúe pensamiento crítico.",
            "options": [
                "Opción A (distractor)",
                "Opción B (distractor)",
                "Opción C <<<CORRECTO>>>",
                "Opción D (distractor)"
            ],
            "explanation": "Explicación didáctica basada en lo mostrado en el video."
        }}
    ]
}}

Reglas del Quiz:
- Crea EXACTAMENTE {num_questions} preguntas.
- Cada pregunta debe tener exactamente 4 opciones de respuesta.
- MARCA la opción correcta agregando "<<<CORRECTO>>>" al final de su texto.
- Solo UNA opción debe tener "<<<CORRECTO>>>".
- NO incluyas el campo "correct_option" en el JSON.
- Las opciones incorrectas deben ser distractores creíbles pero claramente erróneos.
- RECUERDA: Tanto el resumen como las preguntas y explicaciones deben hablar explícitamente del "video".
Todo el contenido generado debe estar en el mismo idioma predominante de la transcripción original."""

            response = self._model.generate_content(prompt)
            result = self._parse_json_response(response.text)

            summary_data = result.get('summary', {})
            if not isinstance(summary_data, dict):
                summary_data = {}

            quiz_raw = result.get('quiz', [])
            quiz_questions = self._extract_quiz_questions(quiz_raw) if isinstance(quiz_raw, list) else []

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

    def generate_summary_only(self, lesson_or_text) -> dict:
        self._initialize()
        transcription_text = self._get_transcription_text(lesson_or_text)
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

    def generate_quiz_only(self, lesson_or_text, num_questions: int = 8) -> list:
        self._initialize()
        transcription_text = self._get_transcription_text(lesson_or_text)
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
        "options": [
            "Opción A (distractor)",
            "Opción B (distractor)",
            "Opción C <<<CORRECTO>>>",
            "Opción D (distractor)"
        ],
        "explanation": "Explicación basada en el video."
    }}
]

IMPORTANTE: Marca la opción correcta agregando "<<<CORRECTO>>>" al final de su texto. NO incluyas el campo "correct_option".""" 

            response = self._model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            
            return self._extract_quiz_questions(result) if isinstance(result, list) else []
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
