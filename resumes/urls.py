from django.urls import path

from . import views

app_name = "resumes"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("resumes/new/", views.create_resume, name="create"),
    path("resumes/<uuid:pk>/edit/basic/", views.builder_basic, name="builder_basic"),
    path("resumes/<uuid:pk>/edit/experience/", views.builder_experience, name="builder_experience"),
    path("resumes/<uuid:pk>/edit/education/", views.builder_education, name="builder_education"),
    path("resumes/<uuid:pk>/edit/skills/", views.builder_skills, name="builder_skills"),
    path("resumes/<uuid:pk>/edit/projects/", views.builder_projects, name="builder_projects"),
    path("resumes/<uuid:pk>/edit/design/", views.builder_design, name="builder_design"),
    path("resumes/<uuid:pk>/preview/", views.preview_resume, name="preview"),
    path("resumes/<uuid:pk>/duplicate/", views.duplicate_resume, name="duplicate"),
    path("resumes/<uuid:pk>/delete/", views.delete_resume, name="delete"),
    path("explore/", views.explore, name="explore"),
    path("r/<str:slug>/pdf/", views.download_pdf, name="pdf"),
    path("r/<str:slug>/", views.public_resume, name="public"),
]
