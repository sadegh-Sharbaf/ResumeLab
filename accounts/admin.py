from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-created_at",)
    list_display = ("username", "email", "phone", "is_staff", "is_active", "created_at")
    search_fields = ("username", "email", "phone", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("اطلاعات", {"fields": ("first_name", "last_name", "email", "phone")}),
        ("دسترسی", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("تاریخ‌ها", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "email", "phone", "password1", "password2")}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "updated_at")
    search_fields = ("user__username", "user__email", "city")
