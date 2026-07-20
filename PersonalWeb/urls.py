from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import healthcheck

urlpatterns = [
    path("healthz/", healthcheck, name="healthcheck"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("personalapp.urls")),
    path("", include("resumes.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
