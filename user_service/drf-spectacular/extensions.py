from drf_spectacular.extensions import OpenApiAuthenticationExtension

class JWTBearerRefreshTokenScheme(OpenApiAuthenticationExtension):
    target_class = ''  # leave empty because you have no `authentication_classes`
    name = 'BearerAuth'  # must match SPECTACULAR_SETTINGS['SECURITY_SCHEMES']

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'JWT Refresh Token in Authorization header using Bearer scheme',
        }
