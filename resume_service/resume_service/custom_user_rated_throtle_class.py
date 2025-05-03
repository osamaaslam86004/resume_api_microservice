from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.cache import caches


class CustomAnonRateThrottle(AnonRateThrottle):
    cache = caches["alternate"]

    def allow_request(self, request, view):
        allowed = super().allow_request(request, view)
        if not request.user.is_authenticated:
            request.rate_limit = {
                "X-RateLimit-Limit": self.get_rate(),
                "X-RateLimit-Remaining": self.num_requests - len(self.history),
            }

            # OR this is another method
            # request.META["HTTP_X_RATELIMIT_LIMIT"] = self.get_rate()
            # request.META["HTTP_X_RATELIMIT_REMAINING"] = self.num_requests - len(
            #     self.history
            # )

        return allowed

    def get_rate(self):
        # print(
        #     f"anon rate -------------------------: {self.THROTTLE_RATES.get('anon', None)}"
        # )
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

            # OR this is another method
            # request.META["HTTP_X_RATELIMIT_LIMIT"] = self.get_rate()
            # request.META["HTTP_X_RATELIMIT_REMAINING"] = self.num_requests - len(
            #     self.history
            # )
        return allowed

    def get_rate(self):
        # Use the scope to retrieve the appropriate rate from settings
        # print(
        #     f"user rate -------------------------: {self.THROTTLE_RATES.get('user', None)}"
        # )
        return self.THROTTLE_RATES.get(self.scope, None)
