from django.urls import path

from certificates.views import (
    DownloadCertificateView,
    GenerateCertificateView,
    MyCertificatesView,
)

urlpatterns = [
    path("certificates/my-certificates/", MyCertificatesView.as_view(), name="my-certificates"),
    path("certificates/courses/<int:course_id>/generate/", GenerateCertificateView.as_view(), name="generate-certificate"),
    path("certificates/<str:code>/download/", DownloadCertificateView.as_view(), name="download-certificate"),
]
