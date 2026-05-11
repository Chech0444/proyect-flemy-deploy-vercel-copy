"""
Servicio de Inteligencia Artificial.

Usa la API de Google Gemini (GRATIS) para:
- Generar resúmenes estructurados de transcripciones
- Generar preguntas tipo quiz con opciones múltiples

API Key gratis en: https://aistudio.google.com/apikey
- Límites del tier gratuito (Gemini 3 Flash):
- 15 requests por minuto
- 1 millón de tokens por minuto
- 2,000 requests por día
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
            self._model = genai.GenerativeModel('gemini-3-flash-preview')
            self._is_configured = True
            logger.info('Google Gemini API inicializada correctamente')
        except Exception as e:
            logger.error(f'Error al inicializar Gemini API: {e}')
            self._is_configured = False

    def _parse_json_response(self, text: str) -> dict | list:
        """
        Extrae JSON de la respuesta de Gemini.
        
        Gemini a veces envuelve el JSON en bloques de código markdown,
        este método maneja esos casos.
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

    def generate_summary(self, transcription_text: str) -> dict:
        """
        Genera un resumen estructurado de una transcripción.
        
        Usa Google Gemini para analizar el texto y generar:
        - Un resumen conciso del contenido
        - Una lista de puntos clave
        
        Args:
            transcription_text: Texto completo de la transcripción.
            
        Returns:
            Dict con:
            - 'content': Resumen en texto
            - 'key_points': Lista de puntos clave
        """
        self._initialize()

        if not self._is_configured:
            return self._fallback_summary(transcription_text)

        try:
            prompt = f"""Eres un creador de contenido educativo y pedagogo experto. 
Analiza la siguiente transcripción de un video educativo y genera un resumen altamente detallado, estructurado y profesional que un estudiante universitario usaría como guía de estudio definitiva.

TRANSCRIPCIÓN:
---
{transcription_text[:12000]}
---

Responde ÚNICAMENTE con un JSON válido (sin bloques de código markdown, sin texto adicional a su alrededor) con esta estructura exacta y llaves:
{{
    "content": "Un resumen exhaustivo y fluido. Explica el contexto inicial, el desarrollo profundo de las ideas principales, las metodologías o ejemplos mencionados en el video (si existen), y la conclusión final. Escribe entre 4 y 7 párrafos nutridos, con un lenguaje profesional y retención de todos los datos técnicos importantes.",
    "key_points": [
        "Concepto Clave 1: Explicación a profundidad de la primera idea o término fundamental debatido.",
        "Concepto Clave 2: Explicación detallada de la segunda idea o término clave.",
        "Concepto Clave 3: Análisis del tercer punto técnico, con su justificación.",
        "Concepto Clave 4: ...",
        "Concepto Clave 5: ... (pueden ser más si el contenido es largo)"
    ]
}}

Asegúrate de que el contenido no sea superficial; profundiza todo lo que la transcripción te permita. Redacta la respuesta final en el mismo idioma predominante de la transcripción original."""

            response = self._model.generate_content(prompt)
            result = self._parse_json_response(response.text)

            logger.info('Resumen generado exitosamente con Gemini')
            return {
                'content': result.get('content', ''),
                'key_points': result.get('key_points', [])
            }

        except Exception as e:
            logger.error(f'Error al generar resumen con Gemini: {e}')
            logger.info('Usando modo fallback para el resumen')
            return self._fallback_summary(transcription_text)

    def generate_quiz(self, transcription_text: str, num_questions: int = 5) -> list:
        """
        Genera preguntas de quiz a partir de una transcripción.
        
        Usa Google Gemini para crear preguntas de opción múltiple
        basadas en el contenido del video.
        
        Args:
            transcription_text: Texto completo de la transcripción.
            num_questions: Número de preguntas a generar (mínimo 5).
            
        Returns:
            Lista de dicts, cada uno con:
            - 'question': Texto de la pregunta
            - 'options': Lista de 4 opciones
            - 'correct_option': Índice de la correcta (0-3)
            - 'explanation': Explicación de la respuesta
        """
        self._initialize()
        num_questions = max(num_questions, 5)

        if not self._is_configured:
            return self._fallback_quiz(transcription_text, num_questions)

        try:
            prompt = f"""Eres un catedrático universitario experto en diseño de evaluaciones y metodologías psicométricas.
Analiza la siguiente transcripción de un video educativo y diseña EXACTAMENTE {num_questions} preguntas de opción múltiple de nivel muy avanzado para evaluar el pensamiento crítico y la comprensión conceptual de alto nivel.

Las opciones incorrectas deben ser "distractores" sumamente plausibles formulados con terminología real extraída del texto, de manera que solo quien comprendió a profundidad el tema consiga acertar. No crees opciones triviales orientadas al descarte fácil.

TRANSCRIPCIÓN:
---
{transcription_text[:12000]}
---

Responde ÚNICAMENTE con un JSON válido (sin bloques de código markdown ni texto adicional).
Debe ser obligatoriamente una lista de diccionarios, con esta estructura y sintaxis exacta:
[
    {{
        "question": "Pregunta compleja que plantee escenarios o analice relaciones de causalidad mencionadas en la lección.",
        "options": [
            "Opción A estructurada e inteligente (distractor 1, malentendido común)",
            "Opción B argumentada (distractor 2, dato real pero irrelevante)",
            "Opción C (respuesta verdadera, clara e indiscutible)",
            "Opción D (distractor 3, conceptualmente tramposa)"
        ],
        "correct_option": 2,
        "explanation": "Explicación didáctica y robusta de por qué esta es la única respuesta correcta, rebatiendo sutilmente el error detrás de los distractores."
    }}
]

Reglas inviolables:
- Exactamente {num_questions} preguntas.
- Todas las preguntas tienen exactamente 4 opciones. Las opciones deben ser de longitudes similares entre sí para evitar sesgos lógicos.
- "correct_option" debe ser estrictamente un entero (0 para A, 1 para B, 2 para C, 3 para D).
- Debes alterar aleatoriamente la ubicación de la respuesta correcta.
- Todo (preguntas, opciones y explicación) tiene que ser devuelto en el mismo idioma de la transcripción proporcionada."""

            response = self._model.generate_content(prompt)
            result = self._parse_json_response(response.text)

            # Validar estructura
            if not isinstance(result, list):
                raise ValueError('La respuesta no es una lista de preguntas')

            questions = []
            for q in result:
                if all(k in q for k in ['question', 'options', 'correct_option']):
                    questions.append({
                        'question': q['question'],
                        'options': q['options'][:4],
                        'correct_option': min(q['correct_option'], 3),
                        'explanation': q.get('explanation', '')
                    })

            if len(questions) < num_questions:
                logger.warning(
                    f'Gemini generó {len(questions)} preguntas, '
                    f'se solicitaron {num_questions}'
                )

            logger.info(f'{len(questions)} preguntas de quiz generadas con Gemini')
            return questions

        except Exception as e:
            logger.error(f'Error al generar quiz con Gemini: {e}')
            logger.info('Usando modo fallback para el quiz')
            return self._fallback_quiz(transcription_text, num_questions)

    # ===================================================
    # Métodos de fallback (cuando no hay API key)
    # ===================================================

    def _fallback_summary(self, transcription_text: str) -> dict:
        """
        Genera un resumen básico sin IA como fallback.
        Extrae las primeras oraciones como resumen.
        """
        sentences = transcription_text.replace('...', '.').split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        # Tomar las primeras oraciones como resumen
        summary_sentences = sentences[:min(8, len(sentences))]
        content = '. '.join(summary_sentences) + '.'

        # Los puntos clave son las oraciones más largas (asumiendo más contenido)
        sorted_sentences = sorted(sentences, key=len, reverse=True)
        key_points = [s.strip() + '.' for s in sorted_sentences[:5]]

        return {
            'content': content,
            'key_points': key_points
        }

    def _fallback_quiz(self, transcription_text: str, num_questions: int) -> list:
        """
        Genera preguntas básicas sin IA como fallback.
        Crea preguntas genéricas basadas en fragmentos del texto.
        """
        sentences = transcription_text.replace('...', '.').split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]

        questions = []
        for i in range(min(num_questions, len(sentences))):
            sentence = sentences[i]
            words = sentence.split()
            if len(words) < 5:
                continue

            # Crear pregunta genérica
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

        # Si no hay suficientes preguntas, completar
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
