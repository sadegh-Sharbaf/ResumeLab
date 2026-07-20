from resumes.models import Resume


def site_context(request):
    featured = (
        Resume.objects.filter(
            is_featured=True,
            status=Resume.Status.PUBLISHED,
            visibility=Resume.Visibility.PUBLIC,
        )
        .only("full_name", "slug")
        .first()
    )
    return {"site_featured_resume": featured}
