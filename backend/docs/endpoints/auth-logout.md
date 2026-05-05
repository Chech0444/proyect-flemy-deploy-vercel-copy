# POST /api/v1/auth/logout/

Invalida el `refresh token` mediante blacklist.

Body JSON:

```json
{
  "refresh": "token_refresh"
}
```
