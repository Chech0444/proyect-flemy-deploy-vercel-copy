from celery import shared_task
from .services import generate_transcription_text, generate_exercise_payload
from courses.models import Lesson
from users.models import Notification, NotificationType, User
import json

@shared_task
def process_lesson_ai_task(lesson_id, user_id):
    """
    Tarea asíncrona para procesar una lección con IA.
    Genera transcripción y ejercicios, y notifica al usuario.
    """
    try:
        lesson = Lesson.objects.get(id=lesson_id)
        user = User.objects.get(id=user_id)
        
        # 1. Generar Transcripción
        transcription = generate_transcription_text(lesson)
        lesson.content = f"{lesson.content}\n\n[TRANSCRIPCIÓN IA]:\n{transcription}"
        lesson.save()
        
        # 2. Generar Ejercicios
        exercises_raw = generate_exercise_payload(lesson)
        # Aquí se guardarían los ejercicios en su modelo correspondiente
        
        # 3. Notificar al usuario
        Notification.objects.create(
            user=user,
            type=NotificationType.SYSTEM,
            title="Procesamiento de IA Completo",
            message=f"La IA ha terminado de analizar la lección: {lesson.title}. ¡Ya puedes revisar la transcripción y los ejercicios!",
            action_url=f"/learning/{lesson.course.slug}"
        )
        
        return f"Éxito procesando lección {lesson_id}"
    except Exception as e:
        return f"Error en tarea de IA: {str(e)}"
