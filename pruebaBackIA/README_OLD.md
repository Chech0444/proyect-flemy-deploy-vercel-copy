# 🎓 Plataforma de Cursos Online - Backend

Backend completo en **Django REST Framework** para una plataforma de cursos online con **procesamiento automático de videos usando IA**.

## ✨ Características

- 📹 **Subida de videos** con validación de formato y tamaño
- 🎵 **Extracción automática de audio** (FFmpeg)
- 📝 **Transcripción automática** con OpenAI Whisper
- 🤖 **Resumen inteligente** con Google Gemini (gratis)
- ❓ **Generación de quiz** (5+ preguntas) con Google Gemini
- ⚡ **Procesamiento en segundo plano** con Celery + Redis
- 📊 **Tracking de progreso** en tiempo real
- 🏗️ **Arquitectura modular** en capas (views, services, models)

## 🏗️ Arquitectura

```
┌─────────────┐     ┌──────────────────────────┐     ┌────────────────┐
│   Cliente    │────▶│  Django REST Framework   │────▶│  PostgreSQL    │
│   (API)      │     │  Views → Services → ORM  │     │  (Base datos)  │
└─────────────┘     └───────────┬──────────────┘     └────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │   Celery Worker      │
                    │                      │
                    │  1. FFmpeg (audio)   │◀──── Redis (broker)
                    │  2. Whisper (texto)  │
                    │  3. Gemini (resumen) │
                    │  4. Gemini (quiz)    │
                    └──────────────────────┘
```

## 📋 Requisitos Previos

| Software | Versión Mínima | Instalación |
|----------|---------------|-------------|
| Python | 3.10+ | [python.org](https://www.python.org/) |
| Docker & Docker Compose | 24+ | [docker.com](https://www.docker.com/) |
| FFmpeg | 4.0+ | `sudo apt install ffmpeg` |

## 🚀 Instalación y Ejecución

### Paso 1: Clonar y Configurar Variables de Entorno

```bash
cd pruebaBackIA
cp .env.example .env
```

Editar `.env` y configurar:
- **GEMINI_API_KEY**: Tu API key de Google Gemini (gratis)
  - Obtén tu key en: https://aistudio.google.com/apikey
  - Es gratis, instantáneo, y no necesita tarjeta de crédito

### Paso 2: Iniciar Servicios (PostgreSQL + Redis)

```bash
docker compose up -d
```

Verificar que los servicios están corriendo:
```bash
docker compose ps
```

### Paso 3: Crear Entorno Virtual e Instalar Dependencias

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
# ó
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### Paso 4: Migrar Base de Datos

```bash
python manage.py makemigrations courses
python manage.py migrate
```

### Paso 5: Crear Superusuario (para el panel admin)

```bash
python manage.py createsuperuser
```

### Paso 6: Iniciar el Servidor Django

```bash
python manage.py runserver
```

### Paso 7: Iniciar el Worker de Celery (en otra terminal)

```bash
source venv/bin/activate
celery -A config worker --loglevel=info
```

✅ **¡Listo!** La API está en `http://localhost:8000/api/v1/`

---

## 📡 API - Endpoints

### Información de la API

```
GET /api/v1/
```

### Cursos

```bash
# Listar cursos
GET /api/v1/courses/

# Crear curso
POST /api/v1/courses/
Content-Type: application/json
{
    "title": "Introducción a Machine Learning",
    "description": "Curso completo de ML desde cero",
    "is_published": true
}

# Detalle de un curso (con lecciones)
GET /api/v1/courses/1/

# Actualizar curso
PUT /api/v1/courses/1/

# Eliminar curso
DELETE /api/v1/courses/1/
```

### Lecciones

```bash
# Listar lecciones de un curso
GET /api/v1/courses/1/lessons/

# Crear lección
POST /api/v1/courses/1/lessons/
Content-Type: application/json
{
    "title": "¿Qué es Machine Learning?",
    "description": "Introducción a los conceptos básicos",
    "order": 1
}

# Detalle de una lección (con video, resumen, preguntas)
GET /api/v1/lessons/1/
```

### Videos

```bash
# Subir video (inicia procesamiento automático)
POST /api/v1/videos/upload/
Content-Type: multipart/form-data
lesson_id: 1
video_file: @mi_video.mp4

# Verificar estado del procesamiento
GET /api/v1/videos/1/status/

# Obtener transcripción
GET /api/v1/videos/1/transcription/

# Obtener resumen (generado por Gemini)
GET /api/v1/videos/1/summary/

# Obtener preguntas del quiz
GET /api/v1/videos/1/quiz/
```

---

## 📦 Ejemplos de Request/Response

### Crear un Curso

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/courses/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Avanzado",
    "description": "Decoradores, generators, async/await y más",
    "is_published": true
  }'
```

**Response:**
```json
{
    "status": "success",
    "message": "Curso creado exitosamente",
    "data": {
        "id": 1,
        "title": "Python Avanzado",
        "description": "Decoradores, generators, async/await y más",
        "thumbnail": null,
        "is_published": true,
        "total_lessons": 0,
        "lessons": [],
        "created_at": "2026-04-24 06:50:00",
        "updated_at": "2026-04-24 06:50:00"
    }
}
```

### Subir un Video

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/videos/upload/ \
  -F "lesson_id=1" \
  -F "video_file=@clase_ml_intro.mp4"
```

**Response:**
```json
{
    "status": "success",
    "message": "Video subido exitosamente. El procesamiento ha iniciado en segundo plano.",
    "data": {
        "video": {
            "id": 1,
            "video_file": "/media/videos/2026/04/24/clase_ml_intro.mp4",
            "original_filename": "clase_ml_intro.mp4",
            "duration": null,
            "file_size": 52428800,
            "uploaded_at": "2026-04-24 06:51:00",
            "processing_status": {
                "id": 1,
                "status": "pending",
                "status_display": "Pendiente",
                "current_step": "waiting",
                "step_display": "En espera",
                "progress_percent": 0,
                "error_message": "",
                "started_at": null,
                "completed_at": null
            }
        },
        "task_id": "abc123-def456",
        "check_status_url": "/api/v1/videos/1/status/"
    }
}
```

### Verificar Estado del Procesamiento

**Request:**
```bash
curl http://localhost:8000/api/v1/videos/1/status/
```

**Response (procesando):**
```json
{
    "status": "success",
    "data": {
        "id": 1,
        "status": "processing",
        "status_display": "Procesando",
        "current_step": "transcribing",
        "step_display": "Transcribiendo",
        "progress_percent": 35,
        "error_message": "",
        "started_at": "2026-04-24 06:51:05",
        "completed_at": null
    }
}
```

**Response (completado):**
```json
{
    "status": "success",
    "data": {
        "id": 1,
        "status": "completed",
        "status_display": "Completado",
        "current_step": "done",
        "step_display": "Finalizado",
        "progress_percent": 100,
        "error_message": "",
        "started_at": "2026-04-24 06:51:05",
        "completed_at": "2026-04-24 06:55:30"
    }
}
```

### Obtener Quiz Generado

**Request:**
```bash
curl http://localhost:8000/api/v1/videos/1/quiz/
```

**Response:**
```json
{
    "status": "success",
    "count": 5,
    "data": [
        {
            "id": 1,
            "question": "¿Qué es Machine Learning?",
            "options": [
                "Un tipo de hardware especializado",
                "Un subcampo de la inteligencia artificial que permite a los sistemas aprender de datos",
                "Un lenguaje de programación",
                "Una base de datos distribuida"
            ],
            "correct_option": 1,
            "explanation": "Machine Learning es un subcampo de la IA donde los sistemas mejoran automáticamente a través de la experiencia y los datos.",
            "created_at": "2026-04-24 06:55:28"
        }
    ]
}
```

---

## 📁 Estructura del Proyecto

```
pruebaBackIA/
├── manage.py                    # Entry point de Django
├── requirements.txt             # Dependencias Python
├── docker-compose.yml           # PostgreSQL + Redis
├── .env.example                 # Template de variables de entorno
├── README.md                    # Esta documentación
│
├── config/                      # Configuración del proyecto
│   ├── __init__.py             # Auto-import de Celery
│   ├── settings.py             # Settings de Django
│   ├── celery.py               # Configuración de Celery
│   ├── urls.py                 # URLs principales
│   └── wsgi.py                 # WSGI config
│
├── apps/                        # Aplicaciones Django
│   └── courses/                # App principal
│       ├── models.py           # Modelos de BD
│       ├── serializers.py      # Serializers DRF (validación)
│       ├── views.py            # Controladores / endpoints
│       ├── urls.py             # Rutas de la API
│       ├── tasks.py            # Tasks de Celery
│       ├── admin.py            # Panel de administración
│       ├── apps.py             # Config de la app
│       ├── services/           # Capa de servicios
│       │   ├── video_processing.py  # FFmpeg + Whisper
│       │   └── ai_services.py      # Google Gemini API
│       └── migrations/         # Migraciones de BD
│
└── media/                       # Archivos subidos
    └── videos/                 # Videos de las lecciones
```

---

## 🤖 Sobre la IA (Google Gemini)

Este proyecto usa **Google Gemini API** (modelo `gemini-3-flash-preview`) para:
- Generar resúmenes estructurados de las transcripciones
- Crear preguntas de quiz con opciones múltiples

### ¿Por qué Gemini?
- ✅ **Completamente gratis** (tier gratuito generoso)
- ✅ **Sin tarjeta de crédito** requerida
- ✅ **15 requests/minuto** en el tier gratuito
- ✅ **1 millón de tokens/minuto**
- ✅ **1,500 requests/día**
- ✅ API key instantánea

### Obtener tu API Key
1. Ve a [Google AI Studio](https://aistudio.google.com/apikey)
2. Inicia sesión con tu cuenta de Google
3. Click en "Create API Key"
4. Copia la key y pégala en tu archivo `.env`

### Fallback sin API Key
Si no configuras la API key, el sistema usará un **modo fallback** que genera resúmenes y preguntas básicas extrayendo información directamente del texto. No es ideal pero el sistema sigue funcionando.

---

## 🔧 Comandos Útiles

```bash
# Ver logs del worker de Celery
celery -A config worker --loglevel=debug

# Abrir shell de Django
python manage.py shell

# Ver migraciones pendientes
python manage.py showmigrations

# Acceder al panel de admin
# http://localhost:8000/admin/

# Parar servicios Docker
docker compose down

# Parar y eliminar datos
docker compose down -v
```

## 📝 Notas Técnicas

- Los videos se procesan **asincrónicamente** con Celery para no bloquear las peticiones HTTP
- Whisper usa el modelo `base` por defecto (balance velocidad/precisión). Puedes cambiarlo a `tiny` (rápido) o `medium`/`large` (preciso) en `.env`
- El audio se extrae en formato WAV 16kHz mono, óptimo para Whisper
- Los archivos temporales de audio se eliminan automáticamente después del procesamiento
- Si un procesamiento falla, Celery reintenta automáticamente hasta 2 veces
