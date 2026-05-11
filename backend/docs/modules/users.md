# Modulo Users

Responsable de autenticacion, autorizacion por rol, perfil y upgrade premium.

## Funcionalidades

- Registro con correo unico y rol por defecto `ROLE_FREE`.
- Login JWT con `access` y `refresh`.
- Logout con blacklist de refresh token.
- Perfil editable con cambio de foto y contrasena.
- Listado de usuarios para administradores.
- Upgrade premium o admin para simulacion de compra.

## Ejecucion

Se carga con `INSTALLED_APPS` y expone rutas bajo `api/v1/`.

Admin: `http://localhost:8000/admin/users/user/`
