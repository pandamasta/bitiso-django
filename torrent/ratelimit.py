from datetime import timedelta
from django.conf import settings
from django.core.cache import caches
from django.core.exceptions import PermissionDenied

# code from https://www.forgepackages.com/guides/rate-limiting-requests

class RateLimitExceeded(PermissionDenied):
    def __init__(self, usage, limit):
        self.usage = usage
        self.limit = limit
        super().__init__("Rate limit exceeded")


class RateLimit:
    def __init__(self, *, key, limit, period, cache=None, key_prefix="rl:", debug=False, request=None):
        self.key = key
        self.limit = limit

        if isinstance(period, timedelta):
            # Can pass a timedelta for convenience
            self.seconds = period.total_seconds()
        else:
            self.seconds = period

        self.cache = cache or caches["default"]
        self.key_prefix = key_prefix
        self.debug = debug or settings.DEBUG
        self.request = request

    def get_client_ip(self):
        if not self.request:
            print("[Debug] No request object provided.")
            return "Unknown IP"

        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
            if not ip:
                print("[Debug] No REMOTE_ADDR in request.META.")
                return "Unknown IP"

        print(f"[Debug] Detected IP: {ip}")
        return ip

    def get_usage(self):
        # Timeout will be set here if it didn't exist, with a starting value of 0
        usage = self.cache.get_or_set(
            self.key_prefix + self.key, 0, timeout=self.seconds
        )

        if self.debug:
            print(f"[RateLimit Debug] Key: {self.key} | Current Usage: {usage} | Client IP: {self.get_client_ip()}")

        return usage

    def increment_usage(self):
        self.cache.incr(self.key_prefix + self.key, delta=1)

        if self.debug:
            print(f"[RateLimit Debug] Key: {self.key} | Incrementing usage by 1")

    def check(self):
        usage = self.get_usage()

        if self.debug:
            print(f"[RateLimit Debug] Key: {self.key} | Checking limit: {self.limit}")

        if usage >= self.limit:
            raise RateLimitExceeded(usage=usage, limit=self.limit)

        self.increment_usage()