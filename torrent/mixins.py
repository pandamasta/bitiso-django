# torrent/mixins.py

from django.http import HttpResponse
from .ratelimit import RateLimit, RateLimitExceeded

class RateLimitMixin:
    """
    Mixin to add rate limiting functionality to views.
    """
    rate_limit_key = ''
    limit = 20  # requests per minute
    period = 60  # period in seconds

    def dispatch(self, request, *args, **kwargs):
        try:
            RateLimit(
                key=f"{request.user.id}:{self.rate_limit_key}",
                limit=self.limit,
                period=self.period,
                request=request,
            ).check()
        except RateLimitExceeded as e:
            return HttpResponse(
                f"Rate limit exceeded. You have used {e.usage} requests, limit is {e.limit}.",
                status=429
            )
        return super().dispatch(request, *args, **kwargs)
