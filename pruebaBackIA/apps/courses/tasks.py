"""
Tasks de Celery - Procesamiento de Video en Segundo Plano.

Define las tareas asíncronas que se ejecutan cuando se sube un video:
1. Extraer audio del video (FFmpeg)
2. Transcribir audio (Whisper)
3. Generar resumen (Google Gemini)
4. Generar preguntas de quiz (Google Gemini)

Cada paso actualiza el estado de procesamiento para que el
frontend pueda mostrar el progreso al usuario.
"""

import logging
from datetime import datetime

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name='courses.process_video',
    max_retries=2,
    default_retry_delay=60,
    acks_late=True
)
def process_video_task(self, video_id: int):
    """
    Task principal de procesamiento de video.
    
    Ejecuta el pipeline completo de procesamiento:
    1. Extrae el audio del video con FFmpeg
    2. Transcribe el audio con Whisper
    3. Genera un resumen con Google Gemini
    4. Genera preguntas de quiz con Google Gemini
    
    Args:
        video_id: ID del modelo Video a procesar.
    """
    # Importar aquí para evitar imports circulares
    from apps.courses.models import (
        Video, Transcription, Summary, QuizQuestion, ProcessingStatus
    )
    from apps.courses.services.video_processing import video_processing_service
    from apps.courses.services.ai_services import ai_service

    audio_path = None

    try:
        # ─────────────────────────────────────────
        # Obtener el video y su estado de procesamiento
        # ─────────────────────────────────────────
        video = Video.objects.get(id=video_id)
        status = video.processing_status
        video_path = video.video_file.path

        logger.info(f'═══ Iniciando procesamiento del video ID={video_id} ═══')
        logger.info(f'Archivo: {video_path}')

        # Actualizar estado: PROCESSING
        status.status = ProcessingStatus.Status.PROCESSING
        status.current_step = ProcessingStatus.Step.EXTRACTING_AUDIO
        status.progress_percent = 0
        status.started_at = timezone.now()
        status.celery_task_id = self.request.id
        status.save()

        # ─────────────────────────────────────────
        # PASO 1: Obtener duración del video
        # ─────────────────────────────────────────
        logger.info('📐 Paso 0: Obteniendo duración del video...')
        duration = video_processing_service.get_video_duration(video_path)
        video.duration = duration
        video.save(update_fields=['duration'])

        # ─────────────────────────────────────────
        # PASO 2: Extraer audio del video
        # ─────────────────────────────────────────
        logger.info('🎵 Paso 1: Extrayendo audio del video...')
        status.current_step = ProcessingStatus.Step.EXTRACTING_AUDIO
        status.progress_percent = 10
        status.save()

        audio_path = video_processing_service.extract_audio(video_path)
        logger.info(f'✅ Audio extraído: {audio_path}')

        status.progress_percent = 25
        status.save()

        # ─────────────────────────────────────────
        # PASO 3: Transcribir audio con Whisper
        # ─────────────────────────────────────────
        logger.info('📝 Paso 2: Transcribiendo audio con Whisper...')
        status.current_step = ProcessingStatus.Step.TRANSCRIBING
        status.progress_percent = 30
        status.save()

        transcription_data = video_processing_service.transcribe_audio(audio_path)

        # Guardar transcripción en la base de datos
        transcription, _ = Transcription.objects.update_or_create(
            video=video,
            defaults={
                'full_text': transcription_data['text'],
                'segments': transcription_data['segments'],
                'language': transcription_data['language']
            }
        )
        logger.info(
            f'✅ Transcripción guardada: {len(transcription_data["text"])} chars'
        )

        status.progress_percent = 50
        status.save()

        # ─────────────────────────────────────────
        # PASO 4: Generar resumen con Gemini
        # ─────────────────────────────────────────
        logger.info('📋 Paso 3: Generando resumen con IA...')
        status.current_step = ProcessingStatus.Step.GENERATING_SUMMARY
        status.progress_percent = 55
        status.save()

        summary_data = ai_service.generate_summary(transcription_data['text'])

        # Guardar resumen en la base de datos
        summary, _ = Summary.objects.update_or_create(
            video=video,
            defaults={
                'content': summary_data['content'],
                'key_points': summary_data['key_points']
            }
        )
        logger.info('✅ Resumen generado y guardado')

        status.progress_percent = 75
        status.save()

        # ─────────────────────────────────────────
        # PASO 5: Generar preguntas de quiz con Gemini
        # ─────────────────────────────────────────
        logger.info('❓ Paso 4: Generando preguntas de quiz con IA...')
        status.current_step = ProcessingStatus.Step.GENERATING_QUIZ
        status.progress_percent = 80
        status.save()

        quiz_data = ai_service.generate_quiz(transcription_data['text'])

        # Eliminar preguntas existentes y crear nuevas
        QuizQuestion.objects.filter(video=video).delete()
        for q_data in quiz_data:
            QuizQuestion.objects.create(
                video=video,
                question=q_data['question'],
                options=q_data['options'],
                correct_option=q_data['correct_option'],
                explanation=q_data.get('explanation', '')
            )
        logger.info(f'✅ {len(quiz_data)} preguntas de quiz creadas')

        # ─────────────────────────────────────────
        # FINALIZACIÓN: Marcar como completado
        # ─────────────────────────────────────────
        status.status = ProcessingStatus.Status.COMPLETED
        status.current_step = ProcessingStatus.Step.DONE
        status.progress_percent = 100
        status.completed_at = timezone.now()
        status.error_message = ''
        status.save()

        logger.info(
            f'═══ Procesamiento completado para video ID={video_id} ═══'
        )

    except Video.DoesNotExist:
        logger.error(f'Video con ID={video_id} no encontrado')
        raise

    except Exception as e:
        # ─────────────────────────────────────────
        # MANEJO DE ERRORES
        # ─────────────────────────────────────────
        error_msg = str(e)
        logger.error(
            f'❌ Error procesando video ID={video_id}: {error_msg}',
            exc_info=True
        )

        try:
            video = Video.objects.get(id=video_id)
            status = video.processing_status
            status.status = ProcessingStatus.Status.ERROR
            status.error_message = error_msg[:1000]
            status.completed_at = timezone.now()
            status.save()
        except Exception:
            logger.error('No se pudo actualizar el estado de error')

        # Reintentar si quedan intentos
        if self.request.retries < self.max_retries:
            logger.info(
                f'Reintentando... (intento {self.request.retries + 1}'
                f'/{self.max_retries})'
            )
            raise self.retry(exc=e)

    finally:
        # ─────────────────────────────────────────
        # LIMPIEZA: Eliminar archivos temporales
        # ─────────────────────────────────────────
        if audio_path:
            video_processing_service.cleanup_audio(audio_path)
