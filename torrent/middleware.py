from django.conf import settings
from django.http import HttpResponse
from torrent.ratelimit import RateLimit, RateLimitExceeded


# __call__(self, request): This method intercepts every incoming request. It checks whether rate limiting is enabled using the setting ENABLE_RATE_LIMITING. If it's disabled, it skips rate limiting altogether.
# RateLimit usage: It creates a RateLimit object using the client's IP or the authenticated user’s ID and checks if the limit is exceeded.
# RateLimitExceeded: If the rate limit is exceeded, it catches this exception and returns an HTTP 429 Too Many Requests response.

class RateLimitMiddleware:
    """
    Middleware that applies rate limiting across views.
    The rate-limiting behavior can be enabled or disabled through settings.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if rate limiting is enabled in settings
        if getattr(settings, 'ENABLE_RATE_LIMITING', True):
            # Construct the rate limit key (IP-based or user-based)
            rate_limit_key = (
                f"{request.user.id}:torrent_list" if request.user.is_authenticated 
                else request.META.get('REMOTE_ADDR', 'unknown_ip')
            )

            # Initialize the RateLimit object
            rate_limiter = RateLimit(
                key=rate_limit_key,
                limit=20,  # Number of requests allowed
                period=60,  # Time period (in seconds)
                request=request,  # Pass the request object for client IP detection
            )

            try:
                # Check if the request exceeds the rate limit
                rate_limiter.check()

            except RateLimitExceeded as e:
                # Return a 429 response if the rate limit is exceeded
                return HttpResponse(
                    f"Rate limit exceeded. You have used {e.usage} requests, limit is {e.limit}.",
                    status=429
                )

        # Continue processing the request if rate limiting is not exceeded
        response = self.get_response(request)
        return response

