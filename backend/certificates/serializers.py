from rest_framework import serializers

from certificates.models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ("id", "course", "code", "generated_at")
