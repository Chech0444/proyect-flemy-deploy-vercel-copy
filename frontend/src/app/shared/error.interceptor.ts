import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { NotificationService } from './notification.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notificationService = inject(NotificationService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'Ha ocurrido un error inesperado';

      if (error.error instanceof ErrorEvent) {
        errorMessage = `Error: ${error.error.message}`;
      } else if (error.error && typeof error.error === 'object') {
        const translations: { [key: string]: string } = {
          'No active account found with the given credentials': 'No se encontró ninguna cuenta activa con estas credenciales.',
          'User is inactive': 'Esta cuenta de usuario está inactiva.',
          'Token is invalid or expired': 'Tu sesión ha expirado. Por favor, inicia sesión de nuevo.',
          'Given token not valid for any token type': 'La sesión no es válida.',
          'Authentication credentials were not provided.': 'No se proporcionaron credenciales de acceso.',
        };

        if (error.error.detail) {
          errorMessage = translations[error.error.detail] || error.error.detail;
        } else {
          const fieldMap: { [key: string]: string } = {
            'username': 'Usuario', 'password': 'Contraseña', 'email': 'Correo electrónico',
            'first_name': 'Nombre', 'last_name': 'Apellido'
          };
          const fieldErrors = Object.entries(error.error)
            .map(([key, value]) => {
              const fieldName = fieldMap[key] || (key.charAt(0).toUpperCase() + key.slice(1));
              const message = Array.isArray(value) ? value[0] : value;
              return `${fieldName}: ${message}`;
            });
          if (fieldErrors.length > 0) errorMessage = fieldErrors.join(' | ');
        }
      } else {
        switch (error.status) {
          case 403: errorMessage = 'No tienes permisos para realizar esta acción'; break;
          case 404: errorMessage = 'El recurso solicitado no existe'; break;
          case 429: errorMessage = 'Demasiadas peticiones. Por favor, intenta más tarde.'; break;
          case 500: errorMessage = 'Error interno del servidor.'; break;
        }
      }

      const isLoginRequest = req.url.includes('/auth/login/');
      if (error.status !== 401 || isLoginRequest) {
        notificationService.showError(errorMessage);
      }
      return throwError(() => error);
    })
  );
};
