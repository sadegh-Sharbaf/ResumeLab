from django.urls import path

from . import views

app_name = "personalapp"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("upload/", views.upload_file, name="upload"),
]
