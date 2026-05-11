# Flemy Backend

Backend completo en Django REST Framework para la aplicacion Flemy. Implementa autenticacion JWT, catalogo y administracion de cursos, progreso del estudiante, gamificacion, certificados, modulo administrativo, documentacion OpenAPI, Docker y PostgreSQL.

## Modulos

- `users`: registro, login JWT, logout con blacklist, perfil, upgrade premium y listado administrativo.
- `courses`: catalogo publico y CRUD administrativo de cursos, secciones y lecciones.
- `learning`: inscripciones, acceso al curso, reproduccion estructurada y progreso.
- `gamification`: racha, XP, leaderboard y nivel.
- `certificates`: generacion y descarga de certificados PDF.
- `ai_tools`: transcripcion, ejercicios, feedback de codigo y chatbot contextual.

## Ejecucion local

```bash
cp .env.example .env
export USE_SQLITE=True
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py bootstrap_admin
python manage.py runserver
```

## Ejecucion con Docker

```bash
cp .env.example .env
docker compose up --build
```

API base: `http://localhost:8000/api/v1/`

Admin Django: `http://localhost:8000/admin/`

Credenciales por defecto del admin local:

- Usuario: `admin`
- Correo: `admin@flemy.local`
- Contrasena: `Admin12345!`

Documentacion Swagger: `http://localhost:8000/api/docs/`

## Documentacion

- Modulos: `docs/modules/`
- Endpoints: `docs/endpoints/`
