from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(request):
    """Used by docker-compose and the pipeline to see that the app is up."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health),
    path("admin/", admin.site.urls),
    path("faculty/", include("faculty.urls")),
]
