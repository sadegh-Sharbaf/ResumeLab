from django.conf import settings
from django.shortcuts import render

from resumes.models import Resume


def home(request):
    featured = (
        Resume.objects.filter(
            is_featured=True,
            status=Resume.Status.PUBLISHED,
            visibility=Resume.Visibility.PUBLIC,
        )
        .prefetch_related("skills", "projects", "social_links")
        .first()
    )
    public_resumes = Resume.objects.filter(
        status=Resume.Status.PUBLISHED,
        visibility=Resume.Visibility.PUBLIC,
        is_listed=True,
    ).exclude(pk=getattr(featured, "pk", None))[:6]
    return render(request, "personalapp/home.html", {"featured": featured, "public_resumes": public_resumes})


def about(request):
    return render(request, "personalapp/about.html")


# Kept as the owner's local phone-to-laptop quick upload helper.
def upload_file(request):
    import os

    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        save_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
        with open(save_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        return render(
            request,
            "personalapp/upload.html",
            {"success": True, "filename": uploaded_file.name},
        )
    return render(request, "personalapp/upload.html")
