# POST /api/v1/ai/exercises/

Genera ejercicios sobre una leccion. Solo `ROLE_ADMIN`.

Body JSON:

```json
{
  "lesson": 1,
  "prompt_context": "Tema a reforzar"
}
```
