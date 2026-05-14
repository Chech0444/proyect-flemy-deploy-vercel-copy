# Flemy - Guía Completa de Instalación y Ejecución

Bienvenido a **Flemy**, tu plataforma de cursos online con procesamiento de video e Inteligencia Artificial (Google Gemini y Whisper).

Esta guía te llevará paso a paso para configurar el proyecto desde cero, ideal si es la **primera vez que lo descargas**.

---

## 🛠️ 1. Requisitos Previos (Instalar antes de empezar)

Asegúrate de tener instalados los siguientes programas en tu sistema:
- **Python 3.10 o superior**
- **Node.js 18 o superior** (viene con `npm`)
- **Docker y Docker Compose** (Para la base de datos y Redis)
- **Git**
- **FFmpeg** (REQUISITO INDISPENSABLE PARA LA IA DE AUDIO/VIDEO):
  - **Windows**: Descarga FFmpeg desde [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) o instálalo vía Winget abriendo tu terminal como administrador: `winget install ffmpeg`. Asegúrate de que quede agregado a tus Variables de Entorno (PATH).
  - **Linux (Ubuntu/Debian)**: Ejecuta `sudo apt update && sudo apt install ffmpeg` en tu terminal.

---

## ⚙️ 2. Configuración Inicial del Backend (Base de Datos y Python)

### A. Variables de Entorno
> ⚠️ **IMPORTANTE**: El archivo `.env` contiene tus claves secretas y **NO se sube a Git**. El repositorio incluye un archivo `.env.example` con todas las variables necesarias y valores de referencia. **Debes copiarlo y configurarlo antes de correr el proyecto.**

1. Entra a la carpeta del backend: `cd backend`
2. Copia el archivo de ejemplo para crear tu entorno local:
   - **Linux/Mac**: `cp .env.example .env`
   - **Windows**: `copy .env.example .env`
3. Abre el archivo `.env` que acabas de crear y configura las siguientes claves:

   **🤖 IA (Gemini):**
   - `GEMINI_API_KEY=` → Pega tu clave de API (gratis en [Google AI Studio](https://aistudio.google.com/apikey))

   **📧 Email (Recuperación de contraseña):**
   - `EMAIL_HOST_USER=` → Tu correo de Gmail (ej: `miflemy@gmail.com`)
   - `EMAIL_HOST_PASSWORD=` → Una **Contraseña de Aplicación** de Google (NO tu contraseña normal de Gmail). Genérala en [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (requiere verificación en 2 pasos activada)
   - `DEFAULT_FROM_EMAIL=` → Mismo correo en formato `Flemy <tu-correo@gmail.com>`

### B. Levantar Infraestructura (Base de Datos PostgreSQL y Redis)
Abre una terminal en la raíz del proyecto y ejecuta:
```bash
cd backend
docker-compose up -d db redis
```
*(Esto descargará y levantará la base de datos y el sistema de caché en segundo plano. La primera vez puede tardar un poco).*

### C. Instalar Dependencias de Python
En la misma terminal del backend, crea y activa un entorno virtual para no afectar otras instalaciones en tu PC:

**En Linux / Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### D. Aplicar Migraciones (Crear tablas en la BD)
Una vez instaladas las librerías, aplica las migraciones para inicializar y rellenar tu base de datos:
```bash
python manage.py migrate
```
*(Opcional: Para acceder al panel de admin, crea tu superusuario escribiendo: `python manage.py createsuperuser` y sigue las instrucciones).*

---

## 🎨 3. Configuración Inicial del Frontend (Angular)

Abre una **nueva terminal** desde la carpeta raíz del proyecto y entra al frontend para instalar las librerías de Node.js:

```bash
cd frontend
npm install
```
*(Este comando descargará todos los módulos necesarios para que la interfaz gráfica funcione correctamente).*

---

## 🚀 4. ¡A Correr el Proyecto! (El Día a Día)

Cada vez que apagues el PC y vayas a trabajar en el proyecto, necesitas abrir **3 terminales independientes** para arrancar las piezas del sistema.

### Terminal 1: El Servidor Backend (Django)
Entra a la carpeta del backend, activa tu entorno y arranca el servidor:
```bash
cd backend
# Activa el entorno (source venv/bin/activate o venv\Scripts\activate)
python manage.py runserver
```

### Terminal 2: El Motor de IA y Procesamiento (Celery Worker)
**Esto es vital** para que funcione el procesamiento de video (Whisper) y la IA de resúmenes y preguntas (Gemini) en segundo plano. 

Abre otra terminal, ve al backend y activa el entorno:
```bash
cd backend
# Activa el entorno (source venv/bin/activate o venv\Scripts\activate)
```
Luego inicia el Worker según tu sistema:
- **En Linux / Mac:** 
  ```bash
  celery -A config worker -l INFO
  ```
- **En Windows:** 
  ```bash
  celery -A config worker -l INFO -P gevent
  ```
  *(Si te da error en Windows, asegúrate de haber instalado gevent ejecutando `pip install gevent` previamente).*

### Terminal 3: La Aplicación Frontend (Angular)
Abre una tercera terminal, ve a la carpeta del frontend y levanta la interfaz visual:
```bash
cd frontend
ng serve
```

---

🎉 **¡Listo!** Una vez ejecutado todo esto, abre **[http://localhost:4200](http://localhost:4200)** en tu navegador y verás toda la plataforma de Flemy funcionando a la perfección con la Inteligencia Artificial integrada.
