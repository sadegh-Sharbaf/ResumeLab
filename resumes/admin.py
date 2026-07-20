from django.contrib import admin

from .models import (
    Certificate,
    Education,
    Experience,
    Interest,
    Language,
    Project,
    Resume,
    Skill,
    SoftSkill,
    SocialLink,
)


class ExperienceInline(admin.StackedInline):
    model = Experience
    extra = 0


class EducationInline(admin.StackedInline):
    model = Education
    extra = 0


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0


class SoftSkillInline(admin.TabularInline):
    model = SoftSkill
    extra = 0


class InterestInline(admin.TabularInline):
    model = Interest
    extra = 0


class ProjectInline(admin.StackedInline):
    model = Project
    extra = 0


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "title", "status", "visibility", "is_listed", "is_featured", "updated_at")
    list_filter = ("status", "visibility", "is_listed", "is_featured", "template", "language")
    search_fields = ("full_name", "job_title", "slug", "user__username", "user__email")
    readonly_fields = ("views_count", "downloads_count", "created_at", "updated_at", "published_at")
    inlines = (ExperienceInline, EducationInline, SkillInline, SoftSkillInline, InterestInline, ProjectInline)


admin.site.register(Language)
admin.site.register(Certificate)
admin.site.register(SocialLink)
