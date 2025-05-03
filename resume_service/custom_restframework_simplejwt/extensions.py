# resume_service/custom_restframework_simplejwt/extensions.py

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class CustomJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "custom_restframework_simplejwt.authentication.JWTStatelessUserAuthentication"  # your auth class path
    name = "BearerAuth"  # must match SECURITY and COMPONENTS settings

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
