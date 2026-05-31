from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


class JWTAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        redirect_url = super().get_login_redirect_url(request)
        user = getattr(request, "user", None)

        print(f"[JWTAdapter] redirect_url from super: {redirect_url}")
        print(f"[JWTAdapter] user: {user}, authenticated: {getattr(user, 'is_authenticated', False)}")
        print(f"[JWTAdapter] FRONTEND_AUTH_CALLBACK_URL: {settings.FRONTEND_AUTH_CALLBACK_URL}")

        if not user or not user.is_authenticated:
            print(f"[JWTAdapter] User NOT authenticated, returning: {redirect_url}")
            return redirect_url

        callback_url = settings.FRONTEND_AUTH_CALLBACK_URL
        redirect_url = self._ensure_frontend_callback(redirect_url, callback_url)
        refresh = RefreshToken.for_user(user)

        final_url = self._append_query_params(
            redirect_url,
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
        )
        print(f"[JWTAdapter] FINAL redirect URL: {final_url[:120]}...")
        return final_url

    def _ensure_frontend_callback(self, redirect_url, callback_url):
        callback = urlparse(callback_url)
        redirect = urlparse(redirect_url)

        if not redirect.netloc:
            return callback_url

        if redirect.scheme != callback.scheme or redirect.netloc != callback.netloc:
            return callback_url

        return redirect_url

    def _append_query_params(self, url, params):
        parsed = urlparse(url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query.update(params)

        return urlunparse(
            parsed._replace(query=urlencode(query))
        )
