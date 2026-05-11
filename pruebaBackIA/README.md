# Plataforma de Cursos Online (Back-End)

Este es el servidor back-end para la plataforma de cursos con procesamiento de video e Inteligencia Artificial (Google Gemini).

## 🚀 Cómo correr el proyecto (Modo Híbrido)

Para mayor velocidad en desarrollo, usamos Docker para la infraestructura y la terminal para el código.

### 1. Configuración de API Key (Gemini)
Antes de empezar, debes configurar tu acceso a la IA:
1.  Abre el archivo `.env` en la raíz del proyecto.
2.  Busca la línea `GEMINI_API_KEY`.
3.  Pega tu clave de API (puedes obtener una gratis en [Google AI Studio](https://aistudio.google.com/apikey)).

### 2. Levantar Infraestructura (Base de Datos y Redis)
Abre una terminal y ejecuta:
```bash
sudo docker-compose up
```
*(Espera a que veas que la base de datos está lista para aceptar conexiones).*

### 3. Levantar el Servidor Web (Django)
Abre otra terminal y ejecuta:
```bash
./venv/bin/python3 manage.py runserver
```
La API estará disponible en: [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)

### 4. Levantar el Procesador (Celery Worker)
Abre una tercera terminal y ejecuta:
```bash
./venv/bin/python3 -m celery -A config worker --loglevel=info
```
*(Esto es necesario para que se procesen los videos y se generen los resúmenes con IA).*

### 5. Probar Integración con IA (Gemini)
Si quieres verificar que tu API Key de Gemini esté funcionando correctamente, ejecuta:
```bash
./venv/bin/python3 test_gemini.py
```
*(Este comando generará un resumen y un quiz de ejemplo para confirmar la conexión).*

---

## 🛠️ Comandos Útiles
- **Crear migraciones:** `./venv/bin/python3 manage.py makemigrations`
- **Aplicar migraciones:** `./venv/bin/python3 manage.py migrate`
- **Crear Superusuario:** `./venv/bin/python3 manage.py createsuperuser`
- **Panel de Admin:** [http://localhost:8000/admin/](http://localhost:8000/admin/)

---
*Para ver la documentación completa y detallada, consulta [README_OLD.md](README_OLD.md)*
