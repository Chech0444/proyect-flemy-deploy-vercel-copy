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


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        # Verificación manual para dar mensajes específicos (soporta username o email)
        if not username or not password:
            return Response(
                {"detail": "Por favor, ingresa tus credenciales."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar usuario por username O por email
        user = User.objects.filter(models.Q(username=username) | models.Q(email=username)).first()
        
        if not user:
            return Response(
                {"detail": "El usuario o correo ingresado no existe en nuestra base de datos."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(password):
            return Response(
                {"detail": "La contraseña ingresada es incorrecta. Por favor, verifica tus datos."},
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


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "El email es requerido"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Obtener el primer usuario en caso de múltiples emails (aunque es unique)
            user = User.objects.filter(email=email).first()
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_link = f"http://localhost:4200/reset-password/{uid}/{token}"
                
                # Simulador de envío de correo en la terminal de Django
                print("\n" + "="*50)
                print("SIMULACRO DE ENVÍO DE EMAIL DE RECUPERACIÓN")
                print(f"Para: {user.email}")
                print("Haz clic en el siguiente enlace para restablecer tu contraseña:")
                print(reset_link)
                print("="*50 + "\n")
        except Exception as e:
            print("Error en Password Reset Request:", e)
            pass
            
        return Response({"message": "Si tu correo está registrado, recibirás un enlace de recuperación."})

class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        uidb64 = request.data.get("uidb64")
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        
        if not uidb64 or not token or not new_password:
            return Response({"error": "Faltan parámetros de seguridad o contraseña"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
            
        if user is not None and default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({"message": "La contraseña ha sido actualizada exitosamente"})
        else:
            return Response(
                {"error": "El enlace de recuperación es inválido, manipulado o ha expirado"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        new_password = request.data.get("new_password")
        if not new_password or len(new_password) < 8:
            return Response(
                {"error": "La nueva contraseña es obligatoria y debe tener al menos 8 caracteres."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        request.user.set_password(new_password)
        request.user.save()
        return Response({"message": "Tu contraseña interna ha sido actualizada correctamente."})

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
    callback_url = "http://localhost:4200"   # Cambia esto en producción
    client_class = OAuth2Client


class GitHubLogin(SocialLoginView):
    """Login con GitHub"""
    adapter_class = GitHubOAuth2Adapter
    callback_url = "http://localhost:4200"
    client_class = OAuth2Client