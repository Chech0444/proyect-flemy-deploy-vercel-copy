from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
import config.admin

from django.views.generic import RedirectView

from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('', RedirectView.as_view(url='admin/', permanent=True)),
    path('admin/', admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/", include("users.urls")),
    path("api/v1/", include("courses.urls")),
    path("api/v1/learning/", include("learning.urls")),
    path("api/v1/gamification/", include("gamification.urls")),
    path("api/v1/certificates/", include("certificates.urls")),
    path("api/v1/billing/", include("billing.urls")),
    path("api/v1/", include("ai_tools.urls")),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
