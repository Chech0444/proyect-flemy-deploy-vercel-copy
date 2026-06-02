from django.db import models
from django.contrib.auth import get_user_model, login
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.permissions import IsAdminRole
from users.serializers import (
    ProfileUpdateSerializer,
    RegisterSerializer,
    UpgradePremiumSerializer,
    UserListSerializer,
    UserProfileSerializer,
)
from learning.services import daily_login_check

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Override que:
    1. Acepta login con username **o** email.
    2. Devuelve mensajes de error claros según la situación.
    3. Actualiza la racha de estudio diario.
    """
    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "").strip()
        password = request.data.get("password")

        # Verificación manual para dar mensajes específicos (soporta username o email)
        if not username or not password:
            return Response(
                {"detail": "Por favor, ingresa tus credenciales."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar usuario por username O por email
        user = User.objects.filter(models.Q(username=username) | models.Q(email=username)).first()
        
        if not user or not user.check_password(password):
            return Response(
                {"detail": "Credenciales inválidas. Verifica tus datos e intenta de nuevo."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"detail": "Tu cuenta está desactivada temporalmente."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Si las credenciales son correctas, ejecutamos el login de sesión y generamos tokens
        try:
            daily_login_check(user)
        except Exception as e:
            print(f"Error no crítico en racha de estudio: {e}")

        # IMPORTANTE: Nos aseguramos de que el 'username' que recibe el validador de JWT 
        # sea el nombre de usuario real, incluso si el usuario ingresó su email.
        mutable_data = request.data.copy()
        mutable_data["username"] = user.username
        request._full_data = mutable_data # Forzar actualización en DRF request
        
        response = super().post(request, *args, **kwargs)
        response.data["is_staff"] = user.is_staff
        return response


# Alias para compatibilidad con users/urls.py
LoginView = CustomTokenObtainPairView


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "El refresh token es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserProfileSerializer(request.user).data)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserListSerializer
    permission_classes = [IsAdminRole]


class UpgradePremiumView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UpgradePremiumSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.role = serializer.validated_data["role"]
        request.user.save(update_fields=["role"])
        return Response(UserProfileSerializer(request.user).data)

from users.models import Notification
from users.serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.notifications.all()[:20]

class NotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            notification = request.user.notifications.get(pk=pk)
            notification.is_read = True
            notification.save(update_fields=["is_read"])
            return Response({"status": "success"})
        except Notification.DoesNotExist:
            return Response({"error": "No encontrada"}, status=status.HTTP_404_NOT_FOUND)

class NotificationReadAllView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return Response({"status": "success"})


# --- Feature: Password Reset via Email Code (from Feature/SantiagoTirado) ---
from users.models import PasswordResetCode
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import random
import string

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "El email es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalizar email
        email = email.strip().lower()
        
        try:
            # Usar iexact por seguridad adicional aunque ya está en lower
            user = User.objects.filter(email__iexact=email).first()
            if user:
                # Generate a 6 digit code
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                
                # Delete any existing valid codes for this user to avoid confusion
                PasswordResetCode.objects.filter(user=user).delete()
                
                # Create a new code
                PasswordResetCode.objects.create(user=user, code=code)
                
                # Configuracion del correo optimizada con HTML
                subject = "Codigo de Recuperacion - Flemy"
                context = {
                    "user": user,
                    "code": code,
                }
                html_message = render_to_string("emails/password_reset.html", context)
                plain_message = strip_tags(html_message)
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user.email]
                
                try:
                    send_mail(
                        subject, 
                        plain_message, 
                        from_email, 
                        recipient_list, 
                        html_message=html_message
                    )
                    print(f"Correo enviado a: {user.email}")
                except Exception as mail_error:
                    print(f"Error al enviar correo real a {user.email}: {mail_error}")
                    # Fallback simulado para desarrollo
                    print(f"\nCÓDIGO DE EMERGENCIA PARA {user.email}: {code}\n")
            else:
                print(f"Password reset solicitado para email no encontrado: {email}")
        except Exception as e:
            print(f"Error crítico en Password Reset Request para {email}: {e}")
            
        return Response({"message": "Si tu correo está registrado, recibirás un código de recuperación."})

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request):
        email = request.data.get("email")
        code = request.data.get("code")
        new_password = request.data.get("new_password")
        
        if not email or not code or not new_password:
            return Response({"error": "Faltan parámetros de seguridad o contraseña"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Normalizar datos
        email = email.strip().lower()
        code = code.strip()
            
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({"error": "El código es inválido o ha expirado"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Find the valid code
        reset_code = PasswordResetCode.objects.filter(user=user, code=code).order_by('-created_at').first()
        
        if reset_code and reset_code.is_valid:
            user.set_password(new_password)
            user.save()
            # Clean up used codes
            PasswordResetCode.objects.filter(user=user).delete()
            return Response({"message": "La contraseña ha sido actualizada exitosamente"})
        else:
            return Response(
                {"error": "El código de recuperación es inválido, manipulado o ha expirado"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password:
            return Response(
                {"error": "Debes ingresar tu contraseña actual."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.check_password(old_password):
            return Response(
                {"error": "La contraseña actual es incorrecta."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not new_password or len(new_password) < 8:
            return Response(
                {"error": "La nueva contraseña debe tener al menos 8 caracteres."},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.user.set_password(new_password)
        request.user.save()
        return Response({"message": "Tu contraseña ha sido actualizada correctamente."})

class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ====================== SOCIAL LOGIN (Google + GitHub) ======================
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


class GoogleLogin(SocialLoginView):
    """Login con Google"""
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.FRONTEND_AUTH_CALLBACK_URL
    client_class = OAuth2Client


class GitHubLogin(SocialLoginView):
    """Login con GitHub"""
    adapter_class = GitHubOAuth2Adapter
    callback_url = settings.FRONTEND_AUTH_CALLBACK_URL
    client_class = OAuth2Client