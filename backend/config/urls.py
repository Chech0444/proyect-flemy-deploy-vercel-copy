from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('', RedirectView.as_view(url='admin/', permanent=True)),
    path('admin/', admin.site.urls),

    # Documentación
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # Apps del proyecto
    path("api/v1/", include("users.urls")),
    path("api/v1/", include("courses.urls")),
    path("api/v1/learning/", include("learning.urls")),
    path("api/v1/gamification/", include("gamification.urls")),
    path("api/v1/certificates/", include("certificates.urls")),
    path("api/v1/billing/", include("billing.urls")),
    path("api/v1/", include("ai_tools.urls")),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # ==================== AUTENTICACIÓN ====================
    path("api/v1/auth/", include("dj_rest_auth.urls")),
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),

    # Social Login (Allauth - Ruta principal)
    path("accounts/", include("allauth.urls")),
]

# Media files en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
