import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { GoogleLoginProvider, SocialAuthServiceConfig } from '@abacritt/angularx-social-login';

import { routes } from './app.routes';
import { authInterceptor } from './shared/auth.interceptor';
import { errorInterceptor } from './shared/error.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor, errorInterceptor])),

    // CONFIGURACIÓN DE GOOGLE LOGIN - ESTO ES LO MÁS IMPORTANTE
    {
      provide: 'SocialAuthServiceConfig',
      useValue: {
        autoLogin: false,
        providers: [
          {
            id: GoogleLoginProvider.PROVIDER_ID,
            provider: new GoogleLoginProvider(
              '182607019164-7toqg4vs5sg3otpae0ikn2rbslbi2sl5.apps.googleusercontent.com'
            )
          }
        ]
      } as SocialAuthServiceConfig
    }
  ]
};