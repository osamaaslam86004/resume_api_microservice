from rest_framework import serializers

# from custom_simplejwt.custom_token_class import CustomSlidingToken
from rest_framework_simplejwt.serializers import (
    TokenObtainSerializer,
    # TokenObtainPairSerializer,
    # TokenBlacklistSerializer,
    # TokenObtainSlidingSerializer,
    # TokenRefreshSlidingSerializer,
)
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from typing import Dict, Any
from django.conf import settings
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from datetime import datetime
from django.utils import timezone
from django.utils.module_loading import import_string
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import default_user_authentication_rule
from rest_framework_simplejwt.exceptions import InvalidToken

# from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken


class CustomTokenObtainSerializer(TokenObtainSerializer):

    def validate(self, attrs: Dict[str, Any]) -> Dict[Any, Any]:
        print(f"attributes {attrs}")
        authenticate_kwargs = {
            self.username_field: attrs["email"],
            "password": attrs["password"],
        }
        print(f"authenticated kwargs {authenticate_kwargs}")
        try:
            authenticate_kwargs["request"] = self.context["request"]
            print(f"authenticate_kwargs['request'] {authenticate_kwargs['request']}")
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)
        print(f"authenticated user {self.user}")

        # fetch the callable from the path specified in SIMPLE_JWT
        USER_AUTHENTICATION_RULE = import_string(
            settings.SIMPLE_JWT["USER_AUTHENTICATION_RULE"]
        )

        if not USER_AUTHENTICATION_RULE(self.user):
            raise AuthenticationFailed(
                detail="User does not exist", code="user_not_found"
            )

        return {}

    @classmethod
    def get_token(cls, user):
        return cls.token_class.for_user(user)  # type: ignore


class CustomTokenObtainPairSerializer(CustomTokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if settings.SIMPLE_JWT["UPDATE_LAST_LOGIN"]:
            update_last_login(None, self.user)

        return data


# Fix: Disable refresh token for inactive user. #814   --> completed
# Add the refresh token to the outstanding db after refreshing #696 --> completed
class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        refresh = self.token_class(attrs["refresh"])

        data = {"access": str(refresh.access_token)}

        if settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"]:
            if settings.SIMPLE_JWT["BLACKLIST_AFTER_ROTATION"]:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()

                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

        auth = JWTAuthentication()
        user = auth.get_user(validated_token=refresh)

        if not default_user_authentication_rule(user):
            return InvalidToken("token not valid because user is inactive")

        refresh.set_jti()
        refresh.set_exp()
        refresh.set_iat()

        OutstandingToken.objects.create(
            user=user,
            jti=refresh[settings.SIMPLE_JWT["JTI_CLAIM"]],
            token=str(refresh),
            created_at=timezone.make_aware(datetime.fromtimestamp(refresh["iat"])),
            expires_at=timezone.make_aware(datetime.fromtimestamp(refresh["exp"])),
        )

        data["refresh"] = str(refresh)

        return data
