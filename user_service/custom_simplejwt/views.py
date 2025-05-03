from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from django.conf import settings


class CustomTokenRefreshView(TokenViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """

    authentication_classes = [JWTStatelessUserAuthentication]
    # _serializer_class works but Do'nt Know why serializer_class not works
    _serializer_class = settings.SIMPLE_JWT["TOKEN_REFRESH_SERIALIZER"]
    http_method_names = [
        "post",
        "options",
    ]  # STATUS 200 FOR "OPTIONS" OR 405 METHOD NOT ALLOWED
    allowed_methods = ["POST", "OPTIONS"]  # RETURNED IN "ALLOW" HEADER

    def add_throttle_headers(self, request, response):
        response["X-RateLimit-Limit"] = request.rate_limit["X-RateLimit-Limit"]
        response["X-RateLimit-Remaining"] = request.rate_limit["X-RateLimit-Remaining"]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        self.add_throttle_headers(request, response)
        return response


class CustomTokenVerifyView(TokenViewBase):
    """
    Takes a token and indicates if it is valid.  This view provides no
    information about a token's fitness for a particular use.
    """

    authentication_classes = [JWTStatelessUserAuthentication]
    # _serializer_class works but Do'nt Know why serializer_class not works
    _serializer_class = settings.SIMPLE_JWT["TOKEN_VERIFY_SERIALIZER"]

    http_method_names = [
        "post",
        "options",
    ]  # STATUS 200 FOR "OPTIONS" OR 405 METHOD NOT ALLOWED
    allowed_methods = ["POST", "OPTIONS"]  # RETURNED IN "ALLOW" HEADER

    def add_throttle_headers(self, request, response):
        response["X-RateLimit-Limit"] = request.rate_limit["X-RateLimit-Limit"]
        response["X-RateLimit-Remaining"] = request.rate_limit["X-RateLimit-Remaining"]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        self.add_throttle_headers(request, response)
        return response
