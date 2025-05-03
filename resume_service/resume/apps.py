from django.apps import AppConfig
from django.db.models.signals import post_save


class ResumeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "resume"

    def ready(self):

        # from .import signals
        import resume.signals
        from custom_restframework_simplejwt.extensions import (
            CustomJWTAuthenticationScheme,
        )
