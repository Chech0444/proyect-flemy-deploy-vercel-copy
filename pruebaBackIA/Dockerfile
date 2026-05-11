# Usar una imagen oficial de Python ligera
FROM python:3.14-slim

# Evitar que Python genere archivos .pyc y permitir logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema indispensables:
# - ffmpeg: para procesar videos
# - postgresql-client y libpq-dev: para conectar con la DB
# - gcc y python3-dev: para compilar algunas librerías
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    postgresql-client \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    libwebp-dev \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . .

# Dar permisos de ejecución al script principal si fuera necesario
# RUN chmod +x manage.py

# Exponer el puerto de Django
EXPOSE 8000
