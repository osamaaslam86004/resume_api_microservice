from django.core.cache import caches
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class CustomAnonRateThrottle(AnonRateThrottle):
    cache = caches["alternate"]

    def allow_request(self, request, view):
        allowed = super().allow_request(request, view)
        if not request.user.is_authenticated:
            request.rate_limit = {
                "X-RateLimit-Limit": self.get_rate(),
                "X-RateLimit-Remaining": self.num_requests - len(self.history),
            }
        return allowed

    def get_rate(self):
        return self.THROTTLE_RATES.get("anon", None)


class CustomUserRateThrottle(UserRateThrottle):
    cache = caches["alternate"]
    scope = "user"

    def allow_request(self, request, view):
        allowed = super().allow_request(request, view)
        if request.user.is_authenticated:
            request.rate_limit = {
                "X-RateLimit-Limit": self.get_rate(),
                "X-RateLimit-Remaining": self.num_requests - len(self.history),
            }
        return allowed

    def get_rate(self):
        return self.THROTTLE_RATES.get(self.scope, None)
