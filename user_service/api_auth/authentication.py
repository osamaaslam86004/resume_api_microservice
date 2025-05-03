import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class CSRFTrustedOriginAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        Authenticate the request based on CSRF_TRUSTED_ORIGINS.
        """
        # Check if the request's origin is allowed in CSRF_TRUSTED_ORIGINS
        origin = request.headers.get("Origin")
        if origin not in getattr(settings, "CSRF_TRUSTED_ORIGINS", []):
            raise AuthenticationFailed("Origin not trusted")

        # Return None, since no user is authenticated with CSRF token
        return None


class Custom_JWTStatelessUserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise AuthenticationFailed("Authorization header missing")

        try:
            prefix, token = auth_header.split(" ")
        except ValueError:
            raise AuthenticationFailed("Invalid Authorization header format")

        if prefix.lower() != "bearer":
            raise AuthenticationFailed("Authorization header must start with Bearer")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        user_id = payload.get("user_id")
        if not user_id:
            raise AuthenticationFailed("Token missing user_id")

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed("User not found")

        return (user, None)


# class Custom_JWTStatelessUserAuthentication(JWTStatelessUserAuthentication):
#     def authenticate(self, request):
#         header = self.get_header(request)
#         if header is None:
#             return None

#         raw_token = self.get_raw_token(header)
#         if raw_token is None:
#             raise AuthenticationFailed("No JWT token provided")

#         validated_token = self.get_validated_token(raw_token)
#         return self.get_user(validated_token), validated_token
