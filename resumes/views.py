from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    CertificateFormSet,
    EducationFormSet,
    ExperienceFormSet,
    InterestFormSet,
    LanguageFormSet,
    ProjectFormSet,
    ResumeBasicForm,
    ResumeDesignForm,
    SkillFormSet,
    SoftSkillFormSet,
    SocialLinkFormSet,
)
from .models import Certificate, Education, Experience, Interest, Language, Project, Resume, Skill, SoftSkill, SocialLink
from .services.pdf import PDFGenerationError, build_resume_pdf


BUILDER_STEPS = (
    ("basic", "اطلاعات اصلی"),
    ("experience", "سوابق شغلی"),
    ("education", "تحصیلات"),
    ("skills", "مهارت و زبان"),
    ("projects", "پروژه و مدارک"),
    ("design", "قالب و انتشار"),
)


def _owner_resume(request, pk):
    return get_object_or_404(Resume, pk=pk, user=request.user)


def _builder_context(resume, current_step, **extra):
    steps = []
    for index, (key, label) in enumerate(BUILDER_STEPS, start=1):
        steps.append(
            {
                "key": key,
                "label": label,
                "number": index,
                "url": reverse(f"resumes:builder_{key}", kwargs={"pk": resume.pk}),
                "active": key == current_step,
            }
        )
    context = {
        "resume": resume,
        "steps": steps,
        "current_step": current_step,
        "step_number": next(item["number"] for item in steps if item["key"] == current_step),
        "step_total": len(steps),
    }
    context.update(extra)
    return context




def _save_ordered_formset(formset):
    """Save a formset and keep its positions contiguous (1, 2, 3, ...)."""
    instances = formset.save()
    queryset = formset.model.objects.filter(resume=formset.instance).order_by("position", "created_at", "pk")
    for index, item in enumerate(queryset, start=1):
        if item.position != index:
            formset.model.objects.filter(pk=item.pk).update(position=index)
    return instances

def _can_view(request, resume):
    if request.user.is_authenticated and resume.user_id == request.user.id:
        return True
    return resume.status == Resume.Status.PUBLISHED and resume.visibility in {
        Resume.Visibility.PUBLIC,
        Resume.Visibility.UNLISTED,
    }


@login_required
def dashboard(request):
    resumes = request.user.resumes.all().prefetch_related("skills", "experiences")
    return render(request, "resumes/dashboard.html", {"resumes": resumes})


@login_required
def create_resume(request):
    resume = Resume.objects.create(
        user=request.user,
        title="رزومه جدید",
        full_name=request.user.get_full_name(),
        email=request.user.email or "",
        phone=request.user.phone or "",
    )
    messages.success(request, "پیش‌نویس رزومه ساخته شد؛ اطلاعاتش را کامل کن.")
    return redirect("resumes:builder_basic", pk=resume.pk)


@login_required
def builder_basic(request, pk):
    resume = _owner_resume(request, pk)
    form = ResumeBasicForm(request.POST or None, request.FILES or None, instance=resume)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "اطلاعات اصلی ذخیره شد.")
        return redirect("resumes:builder_experience", pk=resume.pk)
    return render(request, "resumes/builder_basic.html", _builder_context(resume, "basic", form=form))


@login_required
def builder_experience(request, pk):
    resume = _owner_resume(request, pk)
    formset = ExperienceFormSet(request.POST or None, instance=resume, prefix="experience")
    if request.method == "POST" and formset.is_valid():
        _save_ordered_formset(formset)
        messages.success(request, "سوابق شغلی ذخیره شد.")
        return redirect("resumes:builder_education", pk=resume.pk)
    return render(
        request,
        "resumes/builder_formset.html",
        _builder_context(
            resume,
            "experience",
            page_title="سوابق شغلی",
            page_description="هر سابقه را جدا وارد کن؛ ترتیب نمایش به‌صورت خودکار مدیریت می‌شود.",
            formsets=[{"formset": formset, "title": "سوابق", "prefix": "experience"}],
            next_url=reverse("resumes:builder_education", kwargs={"pk": resume.pk}),
        ),
    )


@login_required
def builder_education(request, pk):
    resume = _owner_resume(request, pk)
    formset = EducationFormSet(request.POST or None, instance=resume, prefix="education")
    if request.method == "POST" and formset.is_valid():
        _save_ordered_formset(formset)
        messages.success(request, "سوابق تحصیلی ذخیره شد.")
        return redirect("resumes:builder_skills", pk=resume.pk)
    return render(
        request,
        "resumes/builder_formset.html",
        _builder_context(
            resume,
            "education",
            page_title="سوابق تحصیلی",
            page_description="دانشگاه، دوره یا آموزش رسمی خودت را اضافه کن.",
            formsets=[{"formset": formset, "title": "تحصیلات", "prefix": "education"}],
            next_url=reverse("resumes:builder_skills", kwargs={"pk": resume.pk}),
        ),
    )


@login_required
def builder_skills(request, pk):
    resume = _owner_resume(request, pk)
    skill_formset = SkillFormSet(request.POST or None, instance=resume, prefix="skill")
    language_formset = LanguageFormSet(request.POST or None, instance=resume, prefix="language")
    soft_skill_formset = SoftSkillFormSet(request.POST or None, instance=resume, prefix="soft_skill")
    interest_formset = InterestFormSet(request.POST or None, instance=resume, prefix="interest")
    formsets = (skill_formset, language_formset, soft_skill_formset, interest_formset)
    if request.method == "POST" and all(formset.is_valid() for formset in formsets):
        for formset in formsets:
            _save_ordered_formset(formset)
        messages.success(request, "مهارت‌ها، زبان‌ها و علاقه‌مندی‌ها ذخیره شدند.")
        return redirect("resumes:builder_projects", pk=resume.pk)
    return render(
        request,
        "resumes/builder_formset.html",
        _builder_context(
            resume,
            "skills",
            page_title="مهارت‌ها، زبان‌ها و علاقه‌مندی‌ها",
            page_description="مهارت‌های فنی، مهارت‌های نرم، زبان‌ها و علاقه‌مندی‌ها را جداگانه اضافه کن.",
            formsets=[
                {"formset": skill_formset, "title": "مهارت‌های فنی", "prefix": "skill"},
                {"formset": language_formset, "title": "زبان‌ها", "prefix": "language"},
                {"formset": soft_skill_formset, "title": "مهارت‌های نرم", "prefix": "soft_skill"},
                {"formset": interest_formset, "title": "علاقه‌مندی‌ها", "prefix": "interest"},
            ],
            next_url=reverse("resumes:builder_projects", kwargs={"pk": resume.pk}),
        ),
    )


@login_required
def builder_projects(request, pk):
    resume = _owner_resume(request, pk)
    project_formset = ProjectFormSet(request.POST or None, instance=resume, prefix="project")
    certificate_formset = CertificateFormSet(request.POST or None, instance=resume, prefix="certificate")
    social_formset = SocialLinkFormSet(request.POST or None, instance=resume, prefix="social")
    valid = project_formset.is_valid() and certificate_formset.is_valid() and social_formset.is_valid()
    if request.method == "POST" and valid:
        _save_ordered_formset(project_formset)
        _save_ordered_formset(certificate_formset)
        _save_ordered_formset(social_formset)
        messages.success(request, "پروژه‌ها، مدارک و لینک‌ها ذخیره شدند.")
        return redirect("resumes:builder_design", pk=resume.pk)
    return render(
        request,
        "resumes/builder_formset.html",
        _builder_context(
            resume,
            "projects",
            page_title="پروژه‌ها، مدارک و لینک‌ها",
            page_description="هر بخش اختیاری است؛ فقط مواردی را که داری اضافه کن.",
            formsets=[
                {"formset": project_formset, "title": "پروژه‌ها", "prefix": "project"},
                {"formset": certificate_formset, "title": "گواهینامه‌ها", "prefix": "certificate"},
                {"formset": social_formset, "title": "شبکه‌های اجتماعی", "prefix": "social"},
            ],
            next_url=reverse("resumes:builder_design", kwargs={"pk": resume.pk}),
        ),
    )


@login_required
def builder_design(request, pk):
    resume = _owner_resume(request, pk)
    form = ResumeDesignForm(request.POST or None, instance=resume)
    if request.method == "POST" and form.is_valid():
        resume = form.save(commit=False)
        if resume.status == Resume.Status.PUBLISHED and not resume.published_at:
            resume.published_at = timezone.now()
        resume.save()
        messages.success(request, "تنظیمات رزومه ذخیره شد.")
        return redirect("resumes:preview", pk=resume.pk)
    return render(request, "resumes/builder_design.html", _builder_context(resume, "design", form=form))


@login_required
def preview_resume(request, pk):
    resume = _owner_resume(request, pk)
    return render(request, "resumes/public_resume.html", {"resume": resume, "is_preview": True})


def public_resume(request, slug):
    resume = get_object_or_404(
        Resume.objects.select_related("user").prefetch_related(
            "experiences", "educations", "skills", "soft_skills", "interests", "languages", "projects", "certificates", "social_links"
        ),
        slug=slug,
    )
    if not _can_view(request, resume):
        raise Http404
    if not (request.user.is_authenticated and request.user.id == resume.user_id):
        Resume.objects.filter(pk=resume.pk).update(views_count=F("views_count") + 1)
    return render(request, "resumes/public_resume.html", {"resume": resume, "is_preview": False})


def explore(request):
    query = request.GET.get("q", "").strip()
    resumes = Resume.objects.filter(
        status=Resume.Status.PUBLISHED,
        visibility=Resume.Visibility.PUBLIC,
        is_listed=True,
    ).select_related("user")
    if query:
        resumes = resumes.filter(
            Q(full_name__icontains=query)
            | Q(job_title__icontains=query)
            | Q(skills__name__icontains=query)
        ).distinct()
    return render(request, "resumes/explore.html", {"resumes": resumes, "query": query})


def download_pdf(request, slug):
    resume = get_object_or_404(
        Resume.objects.select_related("user").prefetch_related(
            "experiences", "educations", "skills", "soft_skills", "interests", "languages", "projects", "certificates", "social_links"
        ),
        slug=slug,
    )
    if not _can_view(request, resume):
        raise Http404

    try:
        pdf = build_resume_pdf(resume)
    except PDFGenerationError as exc:
        return HttpResponse(f"PDF generation failed: {exc}", status=500, content_type="text/plain; charset=utf-8")

    Resume.objects.filter(pk=resume.pk).update(downloads_count=F("downloads_count") + 1)
    response = HttpResponse(pdf, content_type="application/pdf")
    safe_slug = resume.slug.encode("ascii", "ignore").decode() or str(resume.pk)
    response["Content-Disposition"] = f'attachment; filename="resume-{safe_slug}.pdf"'
    return response


@login_required
@require_POST
def duplicate_resume(request, pk):
    original = _owner_resume(request, pk)
    with transaction.atomic():
        duplicated = Resume.objects.create(
            user=request.user,
            title=f"کپی {original.title}",
            full_name=original.full_name,
            job_title=original.job_title,
            summary=original.summary,
            birth_date=original.birth_date,
            marital_status=original.marital_status,
            military_status=original.military_status,
            email=original.email,
            phone=original.phone,
            alternate_phone=original.alternate_phone,
            location=original.location,
            website=original.website,
            language=original.language,
            template=original.template,
            accent_color=original.accent_color,
            show_email=original.show_email,
            show_phone=original.show_phone,
        )
        relation_map = (
            (original.experiences.all(), Experience),
            (original.educations.all(), Education),
            (original.skills.all(), Skill),
            (original.soft_skills.all(), SoftSkill),
            (original.interests.all(), Interest),
            (original.languages.all(), Language),
            (original.projects.all(), Project),
            (original.certificates.all(), Certificate),
            (original.social_links.all(), SocialLink),
        )
        for items, model in relation_map:
            clones = []
            for item in items:
                item.pk = None
                item.resume = duplicated
                clones.append(item)
            model.objects.bulk_create(clones)
    messages.success(request, "یک کپی خصوصی از رزومه ساخته شد.")
    return redirect("resumes:builder_basic", pk=duplicated.pk)


@login_required
def delete_resume(request, pk):
    resume = _owner_resume(request, pk)
    if request.method == "POST":
        title = resume.title
        resume.delete()
        messages.info(request, f"«{title}» حذف شد.")
        return redirect("resumes:dashboard")
    return render(request, "resumes/confirm_delete.html", {"resume": resume})
