import pytest
from core.middleware import NoCacheMiddleware
from django.http import HttpResponse
from django.test import RequestFactory


@pytest.fixture
def middleware():
    return NoCacheMiddleware(lambda request: HttpResponse())


def test_no_cache_headers_added(middleware, request):
    factory = RequestFactory()
    request = factory.get("/some-path/")

    response = middleware(request)

    assert "no-cache" in response["Cache-Control"]
    assert "no-store" in response["Cache-Control"]
    assert "must-revalidate" in response["Cache-Control"]
    assert "max-age=0" in response["Cache-Control"]
