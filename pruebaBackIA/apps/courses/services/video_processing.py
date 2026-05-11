"""
Servicio de Procesamiento de Video.

Maneja la extracción de audio de videos usando FFmpeg/moviepy
y la transcripción de audio usando OpenAI Whisper.
"""

import os
import logging
import tempfile
import subprocess
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


class VideoProcessingService:
    """
    Servicio para procesar videos.
    
    Responsabilidades:
    - Extraer audio de un archivo de video
    - Transcribir audio usando Whisper
    - Obtener la duración del video
    """

    def __init__(self):
        self._whisper_model = None

    @property
    def whisper_model(self):
        """
        Carga lazy del modelo de Whisper.
        Solo se carga la primera vez que se necesita.
        """
        if self._whisper_model is None:
            from faster_whisper import WhisperModel
            model_name = getattr(settings, 'WHISPER_MODEL', 'base')
            logger.info(f'Cargando modelo Whisper: {model_name}')
            self._whisper_model = WhisperModel(model_name, device="cpu", compute_type="int8")
            logger.info(f'Modelo Whisper cargado exitosamente')
        return self._whisper_model

    def get_video_duration(self, video_path: str) -> float:
        """
        Obtiene la duración del video en segundos usando ffprobe.
        
        Args:
            video_path: Ruta absoluta al archivo de video.
            
        Returns:
            Duración en segundos como float.
        """
        try:
            result = subprocess.run(
                [
                    'ffprobe', '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    video_path
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            duration = float(result.stdout.strip())
            logger.info(f'Duración del video: {duration:.2f} segundos')
            return duration
        except Exception as e:
            logger.warning(f'No se pudo obtener la duración del video: {e}')
            return 0.0

    def extract_audio(self, video_path: str) -> str:
        """
        Extrae el audio de un archivo de video usando FFmpeg.
        
        Convierte el audio a formato WAV (16kHz, mono), que es el
        formato óptimo para Whisper.
        
        Args:
            video_path: Ruta absoluta al archivo de video.
            
        Returns:
            Ruta al archivo de audio extraído (.wav).
            
        Raises:
            RuntimeError: Si FFmpeg falla al extraer el audio.
        """
        # Crear archivo temporal para el audio
        audio_dir = os.path.join(settings.MEDIA_ROOT, 'temp_audio')
        os.makedirs(audio_dir, exist_ok=True)

        video_name = Path(video_path).stem
        audio_path = os.path.join(audio_dir, f'{video_name}.wav')

        logger.info(f'Extrayendo audio de: {video_path}')
        logger.info(f'Audio de salida: {audio_path}')

        try:
            # Usar FFmpeg para extraer audio en formato WAV 16kHz mono
            result = subprocess.run(
                [
                    'ffmpeg', '-i', video_path,
                    '-vn',                  # Sin video
                    '-acodec', 'pcm_s16le', # Codec PCM 16-bit
                    '-ar', '16000',         # Sample rate 16kHz (óptimo para Whisper)
                    '-ac', '1',             # Mono
                    '-y',                   # Sobrescribir si existe
                    audio_path
                ],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )

            if result.returncode != 0:
                error_msg = result.stderr[-500:] if result.stderr else 'Error desconocido'
                raise RuntimeError(
                    f'FFmpeg falló al extraer audio: {error_msg}'
                )

            if not os.path.exists(audio_path):
                raise RuntimeError('El archivo de audio no fue creado')

            file_size = os.path.getsize(audio_path)
            logger.info(
                f'Audio extraído exitosamente: {file_size / 1024 / 1024:.2f}MB'
            )
            return audio_path

        except subprocess.TimeoutExpired:
            raise RuntimeError(
                'Timeout al extraer audio del video (>5 minutos)'
            )

    def transcribe_audio(self, audio_path: str) -> dict:
        """
        Transcribe un archivo de audio usando OpenAI Whisper.
        
        Args:
            audio_path: Ruta al archivo de audio (.wav).
            
        Returns:
            Dict con:
            - 'text': Texto completo de la transcripción
            - 'segments': Lista de segmentos con timestamps
            - 'language': Idioma detectado
            
        Raises:
            RuntimeError: Si Whisper falla al transcribir.
        """
        logger.info(f'Transcribiendo audio: {audio_path}')

        try:
            # Ejecutar transcripción con faster-whisper
            segments_gen, info = self.whisper_model.transcribe(
                audio_path,
                beam_size=5
            )

            # Formatear segmentos
            segments = []
            full_text_list = []
            for segment in segments_gen:
                segments.append({
                    'start': round(segment.start, 2),
                    'end': round(segment.end, 2),
                    'text': segment.text.strip()
                })
                full_text_list.append(segment.text.strip())

            transcription_data = {
                'text': " ".join(full_text_list),
                'segments': segments,
                'language': info.language
            }

            logger.info(
                f'Transcripción completada: '
                f'{len(transcription_data["text"])} caracteres, '
                f'{len(segments)} segmentos, '
                f'idioma: {transcription_data["language"]}'
            )
            return transcription_data

        except Exception as e:
            raise RuntimeError(f'Error al transcribir audio: {str(e)}')

    def cleanup_audio(self, audio_path: str):
        """
        Elimina el archivo de audio temporal.
        
        Args:
            audio_path: Ruta al archivo de audio a eliminar.
        """
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                logger.info(f'Archivo temporal eliminado: {audio_path}')
        except Exception as e:
            logger.warning(f'No se pudo eliminar archivo temporal: {e}')


# Instancia singleton del servicio
video_processing_service = VideoProcessingService()
