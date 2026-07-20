import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, password=None, email=None, phone=None, **extra_fields):
        if not username:
            raise ValueError("نام کاربری الزامی است.")
        if not email and not phone:
            raise ValueError("حداقل ایمیل یا شماره تلفن الزامی است.")
        email = self.normalize_email(email) if email else None
        phone = phone.strip() if phone else None
        user = self.model(username=username.strip(), email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, email=None, phone=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True or extra_fields.get("is_superuser") is not True:
            raise ValueError("کاربر مدیر باید دسترسی staff و superuser داشته باشد.")
        return self.create_user(username, password, email=email, phone=phone, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField("نام کاربری", max_length=150, unique=True)
    email = models.EmailField("ایمیل", unique=True, null=True, blank=True)
    phone = models.CharField("شماره تلفن", max_length=20, unique=True, null=True, blank=True)
    first_name = models.CharField("نام", max_length=150, blank=True)
    last_name = models.CharField("نام خانوادگی", max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]
    objects = UserManager()

    class Meta:
        ordering = ("-created_at",)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_short_name(self):
        return self.first_name or self.username

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account_profile")
    avatar = models.ImageField(upload_to="account_avatars/%Y/%m/", blank=True)
    bio = models.TextField("درباره من", blank=True)
    city = models.CharField("شهر", max_length=100, blank=True)
    website = models.URLField("وب‌سایت", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"پروفایل {self.user.username}"
