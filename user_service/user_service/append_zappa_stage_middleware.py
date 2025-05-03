# middleware/append_stage_middleware.py

from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class AppendStageMiddleware:
    """
    Redirect root API Gateway URL to /<stage>/ and ensure trailing slash exists.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.api_gateway_host = settings.ALLOWED_HOSTS[0]
        self.stage = settings.STAGE

    def __call__(self, request):
        host = request.get_host()
        path = request.path
        query_string = request.META.get("QUERY_STRING", "")
        redirect_url = None

        if not settings.DEBUG and host == self.api_gateway_host:
            # 1. Path does not start with stage prefix
            if not path.startswith(f"/{self.stage}/"):
                redirect_url = f"/{self.stage}{path}"
            # 2. Path starts correctly but is missing trailing slash
            elif not path.endswith("/") and "." not in path.split("/")[-1]:
                redirect_url = f"{path}/"

        if redirect_url:
            # Append query string if present
            if query_string:
                redirect_url += f"?{query_string}"
            return HttpResponsePermanentRedirect(redirect_url)

        return self.get_response(request)
