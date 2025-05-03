from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from api_auth.authentication import CustomUser
from custom_simplejwt.serializers import CustomTokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "username", "password", "is_staff", "is_active"]

    def create(self, validated_data):

        user = get_user_model().objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            is_active=validated_data.get("is_active", None),
            is_staff=validated_data.get("is_staff", None),
        )

        return user


class TokenClaimObtainPairSerializer(CustomTokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["user"] = user.username

        return token


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ("old_password", "password", "password2")

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"}
            )
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data["password"])
        instance.save()

        return instance


class LogoutResponseSerializer(serializers.Serializer):
    status = serializers.CharField(
        help_text='Status message, e.g., "Successful Logout"'
    )


class TokenErrorSerializer(serializers.Serializer):
    detail = serializers.CharField(help_text="Token already blacklisted")
    status_code = serializers.IntegerField(help_text="HTTP status code, e.g., 400")


class InternalServerErrorSerializer(serializers.Serializer):
    detail = serializers.CharField(help_text="Server Error")
    status_code = serializers.IntegerField(help_text="HTTP status code, e.g., 500")


class UserExistenceRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(
        required=True, help_text="ID of the user to check."
    )
