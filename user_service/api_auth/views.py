import logging

import jsonschema
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control, cache_page
from django.views.decorators.vary import vary_on_headers
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from jsonschema import ValidationError
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api_auth.custom_user_rated_throtle_class import (
    CustomAnonRateThrottle,
    CustomUserRateThrottle,
)
from api_auth.models import CustomUser
from api_auth.schemas import ValidateJson, user_create_response_schema
from api_auth.serializers import (
    InternalServerErrorSerializer,
    LogoutResponseSerializer,
    TokenClaimObtainPairSerializer,
    TokenErrorSerializer,
    UserExistenceRequestSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema(
    description="End-Point for obtaining Refresh and Access Token",
    request=TokenClaimObtainPairSerializer,
    responses={200: TokenClaimObtainPairSerializer},
    examples=[
        OpenApiExample(
            "Example Response",
            value={"refresh": "string", "access": "string"},
            response_only=True,  # Specifies this example is for responses
            status_codes=["200"],
        )
    ],
    methods=["POST", "OPTIONS"],
)
class MyTokenObtainPairView(TokenObtainPairView):
    http_method_names = [
        "post",
        "options",
    ]  # STATUS 200 FOR "OPTIONS" OR 405 METHOD NOT ALLOWED
    allowed_methods = ["POST", "OPTIONS"]  # RETURNED IN "ALLOW" HEADER
    serializer_class = TokenClaimObtainPairSerializer

    def add_throttle_headers(self, request, response):
        response["X-RateLimit-Limit"] = request.rate_limit["X-RateLimit-Limit"]
        response["X-RateLimit-Remaining"] = request.rate_limit["X-RateLimit-Remaining"]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        self.add_throttle_headers(request, response)
        return response


@method_decorator(cache_control(private=True), name="dispatch")
@method_decorator(cache_page(60 * 60 * 2), name="dispatch")
@method_decorator(vary_on_headers("User-Agent"), name="dispatch")
class UserCreateView(ModelViewSet, ValidateJson):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    http_method_names = [
        "post",
        "options",
    ]  # STATUS 200 FOR "OPTIONS" OR 405 METHOD NOT ALLOWED
    allowed_methods = ["POST", "OPTIONS"]  # RETURNED IN "ALLOW" HEADER
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    throttle_classes = [CustomAnonRateThrottle, CustomUserRateThrottle]
    lookup_url_kwarg = "id"

    def add_throttle_headers(self, request, response):
        response["X-RateLimit-Limit"] = request.rate_limit["X-RateLimit-Limit"]
        response["X-RateLimit-Remaining"] = request.rate_limit["X-RateLimit-Remaining"]

    def initialize_request(self, request, *args, **kwargs):
        self.action = self.action_map.get(request.method.lower())
        return super().initialize_request(request, *args, **kwargs)

    def get_authenticators(self):
        # No authentication required for 'create' action (removes lock in Swagger UI)
        if self.action == "create":
            return []
        # JWT authentication required for 'get_api_user_id_for_user'
        elif self.action == "get_api_user_id_for_user":
            return [JWTStatelessUserAuthentication()]
        return super().get_authenticators()

    # Overriding because by default options methods returns all 6 HTTP-Methods
    # Post, Put, Patch, Get, Head, Options
    def options(self, request, *args, **kwargs):

        response = super().options(request, *args, **kwargs)
        response["Allow"] = "POST", "OPTIONS"
        response["Access-Control-Allow-Methods"] = "POST", "OPTIONS"
        return response

    def create(self, request, *args, **kwargs):
        # Validate request data
        try:
            self.validate_json(request.data)
        except Exception as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        response = super().create(request, *args, **kwargs)

        # # Validate response data
        try:
            jsonschema.validate(response.data, user_create_response_schema)
        except ValidationError as e:
            response = Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except jsonschema.SchemaError as e:
            response = Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        self.add_throttle_headers(request, response)

        return response

    def get_api_user_id_for_user(self, request, *args, **kwargs):

        if (
            "username" in request.data
            and "email" in request.data
            and "password" in request.data
            and request.data["username"]
            and request.data["email"]
            and request.data["password"] is not None
        ):
            username = request.data.get("username")
            email = request.data.get("email")
            password = request.data.get("password")

            print(username)
            print(email)
            print(password)

            try:
                queryset = CustomUser.objects.get_user(email, username, password)
                if queryset:
                    serializer = self.get_serializer(queryset)
                    response = Response(serializer.data)
                    self.add_throttle_headers(request, response)
                    return response

                else:
                    response = Response(
                        {"error": "User does not exist"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                    self.add_throttle_headers(request, response)
                    return response

            except Exception as e:
                response = Response({"error": str(e)})
                self.add_throttle_headers(request, response)
                return response
        else:
            return Response(
                {
                    "keys": "one of the keys is missing from list [username, password, username]",
                    "values": "either email is None or password is None",
                }
            )


class UserExistenceCheckView(APIView):
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    throttle_classes = [CustomAnonRateThrottle]
    authentication_classes = []
    http_method_names = ["post"]
    allowed_methods = ["POST"]

    def add_throttle_headers(self, request, response):
        """
        Add rate limit headers to the response if available.
        """
        if hasattr(request, "rate_limit") and isinstance(request.rate_limit, dict):
            response["X-RateLimit-Limit"] = request.rate_limit.get(
                "X-RateLimit-Limit", ""
            )
            response["X-RateLimit-Remaining"] = request.rate_limit.get(
                "X-RateLimit-Remaining", ""
            )
        return response

    @extend_schema(
        request=UserExistenceRequestSerializer,
        responses={
            200: OpenApiResponse(description="User exists."),
            404: OpenApiResponse(description="User not found."),
            400: OpenApiResponse(description="Bad request. Missing user_id."),
            500: OpenApiResponse(description="Internal server error."),
        },
        methods=["POST"],
        examples=[
            OpenApiExample(
                "Example Response",
                value={"user_id": "1", "user_id": "4231"},
                response_only=True,
                status_codes=["200"],
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        if not user_id:
            response = Response(
                {"detail": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
            self.add_throttle_headers(request, response)
            return response

        try:
            user_exists = CustomUser.objects.filter(id=user_id).exists()
            if user_exists:
                response = Response(
                    {"detail": "User exists."}, status=status.HTTP_200_OK
                )
            else:
                response = Response(
                    {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
                )
            self.add_throttle_headers(request, response)
            return response

        except Exception as e:
            response = Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            self.add_throttle_headers(request, response)
            return response


class LogOutView(APIView):
    authentication_classes = []
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    throttle_classes = [CustomAnonRateThrottle]
    http_method_names = ["get"]
    allowed_methods = ["GET"]

    def add_throttle_headers(self, request, response):
        """
        Add rate limit headers to the response if available.
        """
        if hasattr(request, "rate_limit") and isinstance(request.rate_limit, dict):
            response["X-RateLimit-Limit"] = request.rate_limit.get(
                "X-RateLimit-Limit", ""
            )
            response["X-RateLimit-Remaining"] = request.rate_limit.get(
                "X-RateLimit-Remaining", ""
            )
        return response

    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(
                name="Authorization",
                location=OpenApiParameter.HEADER,
                required=True,
                description="JWT refresh token as Bearer token",
                type=str,
            )
        ],
        responses={
            200: OpenApiResponse(response=LogoutResponseSerializer),
            400: OpenApiResponse(response=TokenErrorSerializer),
            500: OpenApiResponse(response=InternalServerErrorSerializer),
        },
        summary="Logout Endpoint (JWT Refresh Token from Authorization Header)",
    )
    def get(self, request, *args, **kwargs):
        """Logout user by blacklisting refresh token passed via Authorization header"""
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            response = Response(
                {"detail": "Missing or malformed Authorization header"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            self.add_throttle_headers(request, response)
            return response

        refresh_token = auth_header.split(" ")[1]
        token = None

        try:
            token = RefreshToken(refresh_token)
        except TokenError:
            response = Response(
                {"detail": "Invalid or already blacklisted token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
            self.add_throttle_headers(request, response)
            return response

        try:

            token.blacklist()
            response = Response(
                {"status": "Successful Logout"}, status=status.HTTP_200_OK
            )
            self.add_throttle_headers(request, response)
            return response

        except TokenError:
            response = Response(
                {"detail": "Invalid or already blacklisted token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

            self.add_throttle_headers(request, response)
            return response
