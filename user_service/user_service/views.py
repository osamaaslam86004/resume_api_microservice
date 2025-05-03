from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.http import url_has_allowed_host_and_scheme


def maintenance(request):
    return render(request, "503.html", context=None, status=503)


def health_check(request):
    return JsonResponse({"status": "ok"})


def root_redirect(request):
    base_path = request.path
    if not base_path.endswith("/"):
        base_path += "/"

    full_path = f"{base_path}api/schema/swagger-ui/"

    if not settings.DEBUG and url_has_allowed_host_and_scheme(
        full_path, allowed_hosts=settings.ALLOWED_HOSTS
    ):
        return HttpResponseRedirect(full_path)

    return HttpResponseRedirect("/api/schema/swagger-ui/")
