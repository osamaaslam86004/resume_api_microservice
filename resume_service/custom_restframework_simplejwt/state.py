from django.conf import settings
from rest_framework_simplejwt.backends import TokenBackend

api_settings = settings.SIMPLE_JWT

token_backend = TokenBackend(
    api_settings["ALGORITHM"],
    api_settings["SIGNING_KEY"],
    api_settings["VERIFYING_KEY"],
    api_settings["AUDIENCE"],
    api_settings["ISSUER"],
    api_settings["JWK_URL"],
    api_settings["LEEWAY"],
    api_settings["JSON_ENCODER"],
)
