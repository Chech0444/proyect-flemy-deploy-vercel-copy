# Flemy - Guía de Ejecución Rápida

Esta guía contiene únicamente los comandos esenciales para levantar toda la plataforma de manera local. Sigue el orden especificado.

## 1. Contenedores Docker (Base de Datos y Caché)
Para ejecutar la base de datos PostgreSQL y Redis, ve a la carpeta del backend y levanta los servicios:
```bash
cd backend
docker-compose up -d db redis
```

## 2. Backend (Servidor Django)
Abre una **nueva terminal**, activa tu entorno virtual y arranca el servidor web:
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

## 3. Worker de IA / Transcripción (Celery)
Abre **otra terminal** independiente, ve al backend, activa el entorno virtual y levanta Celery. Esto es lo que procesa los videos, la transcripción con Whisper y la IA con Gemini en segundo plano:
```bash
cd backend
source venv/bin/activate
celery -A config worker -l INFO
```

## 4. Frontend (Angular)
Por último, abre una **cuarta terminal**, ve a la carpeta del frontend y levanta la aplicación visual en modo desarrollo:
```bash
cd frontend
ng serve
```

¡Listo! Una vez ejecutado esto, puedes abrir `http://localhost:4200` en tu navegador y verás todo funcionando.
