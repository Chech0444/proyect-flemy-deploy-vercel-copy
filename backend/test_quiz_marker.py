import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django; django.setup()
import json
from courses.services.ai_services import AIService
from courses.models import Course, Section, Lesson

c = Course.objects.filter(title__icontains='Java').first()
s = Section.objects.filter(course=c).first()
lesson = Lesson.objects.filter(section=s).first()

svc = AIService()
svc._initialize()

prompt = '''Eres un catedratico universitario.
Analiza la siguiente transcripcion de un video educativo y genera SOLO un JSON con preguntas de quiz.

TRANSCRIPCION:
{content}

Responde UNICAMENTE con una lista JSON con 2 preguntas:
[
    {{
        "question": "Pregunta",
        "options": [
            "Opcion A (distractor)",
            "Opcion B (distractor)",
            "Opcion C <<<CORRECTO>>>",
            "Opcion D (distractor)"
        ],
        "explanation": "Explicacion."
    }}
]

IMPORTANTE: Marca la opcion correcta con <<<CORRECTO>>>. NO incluyas correct_option.'''

resp = svc._model.generate_content(prompt.format(content=lesson.content[:3000]))
print('RAW RESPONSE:')
print(resp.text[:1500])
print()
print('---')
print('MARKER FOUND:', '<<<CORRECTO>>>' in resp.text)
