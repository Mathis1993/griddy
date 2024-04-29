from django.http import HttpResponse
from django.utils.cache import add_never_cache_headers


class NoCacheMiddleware:
    """
    Middleware to add no-cache headers to all responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request) -> HttpResponse:
        response = self.get_response(request)
        add_never_cache_headers(response)
        return response
