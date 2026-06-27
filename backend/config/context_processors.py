from django.conf import settings


def frontend_url(request):
    callback = getattr(settings, 'FRONTEND_AUTH_CALLBACK_URL', 'http://localhost:4200/auth/callback')
    base = callback.replace('/auth/callback', '')
    return {
        'FRONTEND_URL': base or 'http://localhost:4200',
    }
