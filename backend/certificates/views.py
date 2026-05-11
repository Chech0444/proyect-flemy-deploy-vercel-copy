from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from certificates.models import Certificate
from certificates.serializers import CertificateSerializer
from certificates.services import build_certificate_pdf
from courses.models import Course
from learning.models import Enrollment
from learning.services import compute_course_progress


class MyCertificatesView(generics.ListAPIView):
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Certificate.objects.filter(user=self.request.user).select_related("course")


class GenerateCertificateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        if not Enrollment.objects.filter(user=request.user, course=course).exists():
            raise ValidationError("Debes estar inscrito en el curso.")
        progress = compute_course_progress(request.user, course)
        if progress < 100:
            raise ValidationError("El certificado solo se habilita al completar el 100% del curso.")
        certificate, _ = Certificate.objects.get_or_create(user=request.user, course=course)
        return Response(CertificateSerializer(certificate).data)


class DownloadCertificateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, code):
        certificate = get_object_or_404(Certificate, code=code, user=request.user)
        pdf_file = build_certificate_pdf(certificate)
        return FileResponse(pdf_file, filename=f"certificado-{certificate.code}.pdf")
