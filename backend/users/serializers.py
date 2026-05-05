from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import UserRole

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "password")

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Este correo ya existe.")
        return value.lower()

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data, role=UserRole.FREE)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "photo",
            "bio",
            "preferences",
            "role",
            "xp",
            "study_streak",
            "last_study_date",
            "is_premium",
        )
        read_only_fields = ("role", "xp", "study_streak", "last_study_date", "is_premium")


class ProfileUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "photo", "password", "bio", "preferences")

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
            "date_joined",
            "xp",
            "study_streak",
        )


class UpgradePremiumSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=[UserRole.PREMIUM, UserRole.ADMIN],
        default=UserRole.PREMIUM,
    )

from users.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "type", "title", "message", "is_read", "action_url", "created_at")
        read_only_fields = fields
