from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
    UpgradePremiumView,
    UserListView,
    NotificationListView,
    NotificationReadView,
    NotificationReadAllView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangePasswordView,
    DeleteAccountView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/profile/", ProfileView.as_view(), name="profile"),
    path("auth/profile/change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
    path("auth/profile/delete-account/", DeleteAccountView.as_view(), name="auth-delete-account"),
    path("auth/password-reset/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("auth/password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("auth/notifications/", NotificationListView.as_view(), name="notifications-list"),
    path("auth/notifications/<int:pk>/read/", NotificationReadView.as_view(), name="notification-read"),
    path("auth/notifications/read-all/", NotificationReadAllView.as_view(), name="notification-read-all"),
    path("users/", UserListView.as_view(), name="users-list"),
    path("users/upgrade-premium/", UpgradePremiumView.as_view(), name="upgrade-premium"),
]
