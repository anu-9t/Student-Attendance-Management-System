from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def health(request):
    """Used by docker-compose and the pipeline to see that the app is up."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health),
    path("admin/", admin.site.urls),
    # Each module adds its own urls.py and includes it here as it is built.
]
