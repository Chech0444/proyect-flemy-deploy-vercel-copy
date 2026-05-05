# Pruebas de Endpoints

Esta documentacion resume la suite automatizada que valida los endpoints principales del backend Flemy.

## Ejecucion

```bash
USE_SQLITE_FOR_TESTS=True ./.venv/bin/python manage.py test
```

## Cobertura funcional

- `users/tests.py`: registro, listado admin, actualizacion de perfil y upgrade premium.
- `courses/tests.py`: catalogo publico y creacion de estructura academica por admin.
- `learning/tests.py`: inscripcion, completado de leccion y resumen de progreso.
- `gamification/tests.py`: dashboard y leaderboard.
- `certificates/tests.py`: generacion, listado y descarga de certificado.
- `ai_tools/tests.py`: transcripcion, feedback, chatbot y generacion de ejercicios.

## URL de documentacion

Si levantas el servidor, esta documentacion queda disponible como archivo del proyecto en:

- `/docs/tests/README.md`

Ruta local:

- [docs/tests/README.md](/Users/ArleMorales/Documents/2026/sena/1 trimstre/proyectos/flemy/docs/tests/README.md)
