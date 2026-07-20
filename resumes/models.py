import re
import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Max
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


PERSIAN_MONTHS = (
    "",
    "فروردین",
    "اردیبهشت",
    "خرداد",
    "تیر",
    "مرداد",
    "شهریور",
    "مهر",
    "آبان",
    "آذر",
    "دی",
    "بهمن",
    "اسفند",
)
PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def to_persian_digits(value):
    return str(value or "").translate(PERSIAN_DIGITS)


def format_jalali_date(value, *, always_show_day=False):
    """Return a readable Persian date while keeping invalid legacy values visible."""
    text = str(value or "").strip()
    match = re.fullmatch(r"(\d{4})/(\d{2})/(\d{2})", text)
    if not match:
        return to_persian_digits(text)
    year, month, day = map(int, match.groups())
    if not 1 <= month <= 12:
        return to_persian_digits(text)
    year_text = to_persian_digits(year)
    if day == 1 and not always_show_day:
        return f"{PERSIAN_MONTHS[month]} {year_text}"
    return f"{to_persian_digits(day)} {PERSIAN_MONTHS[month]} {year_text}"


def cleaned_lines(value):
    lines = []
    for raw_line in str(value or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[\s•●▪◦\-*–—]+", "", line)
        line = re.sub(r"^\d+[.)-]\s*", "", line)
        if line:
            lines.append(line)
    return lines


class Resume(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PUBLISHED = "published", "منتشرشده"
        ARCHIVED = "archived", "بایگانی"

    class Visibility(models.TextChoices):
        PRIVATE = "private", "خصوصی"
        UNLISTED = "unlisted", "فقط با لینک"
        PUBLIC = "public", "عمومی"

    class Template(models.TextChoices):
        MODERN = "modern", "مدرن"
        MINIMAL = "minimal", "مینیمال"
        CLASSIC = "classic", "کلاسیک"

    class Language(models.TextChoices):
        FA = "fa", "فارسی"
        EN = "en", "English"

    class MaritalStatus(models.TextChoices):
        SINGLE = "single", "مجرد"
        MARRIED = "married", "متأهل"
        OTHER = "other", "سایر"

    class MilitaryStatus(models.TextChoices):
        COMPLETED = "completed", "پایان خدمت"
        EXEMPT = "exempt", "معافیت"
        IN_SERVICE = "in_service", "در حال خدمت"
        NOT_APPLICABLE = "not_applicable", "مشمول نیست"
        UNSET = "unset", "ذکر نشود"

    ACCENT_CHOICES = (
        ("#8b5cf6", "بنفش"),
        ("#06b6d4", "فیروزه‌ای"),
        ("#2563eb", "آبی"),
        ("#10b981", "سبز"),
        ("#f97316", "نارنجی"),
        ("#e11d48", "قرمز"),
        ("#334155", "خاکستری"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resumes")
    title = models.CharField("عنوان داخلی رزومه", max_length=120, default="رزومه من")
    slug = models.SlugField("نشانی عمومی", max_length=180, unique=True, allow_unicode=True, blank=True)

    full_name = models.CharField("نام و نام خانوادگی", max_length=150)
    job_title = models.CharField("عنوان شغلی", max_length=150, blank=True)
    summary = models.TextField("خلاصه حرفه‌ای", blank=True)
    birth_date = models.CharField("تاریخ تولد", max_length=10, blank=True)
    marital_status = models.CharField("وضعیت تأهل", max_length=20, choices=MaritalStatus.choices, blank=True)
    military_status = models.CharField(
        "وضعیت سربازی", max_length=20, choices=MilitaryStatus.choices, default=MilitaryStatus.UNSET, blank=True
    )
    email = models.EmailField("ایمیل", blank=True)
    phone = models.CharField("تلفن", max_length=30, blank=True)
    alternate_phone = models.CharField("تلفن دوم", max_length=30, blank=True)
    location = models.CharField("محل سکونت", max_length=120, blank=True)
    website = models.URLField("وب‌سایت", blank=True)
    avatar = models.ImageField("تصویر", upload_to="resume_avatars/%Y/%m/", blank=True)

    language = models.CharField("زبان رزومه", max_length=5, choices=Language.choices, default=Language.FA)
    template = models.CharField("قالب", max_length=20, choices=Template.choices, default=Template.MODERN)
    accent_color = models.CharField("رنگ اصلی", max_length=10, choices=ACCENT_CHOICES, default="#8b5cf6")
    status = models.CharField("وضعیت", max_length=20, choices=Status.choices, default=Status.DRAFT)
    visibility = models.CharField("دسترسی", max_length=20, choices=Visibility.choices, default=Visibility.PRIVATE)
    is_listed = models.BooleanField("نمایش در بخش رزومه‌ها", default=False)
    is_featured = models.BooleanField("رزومه ویژه صفحه اصلی", default=False)
    show_email = models.BooleanField("نمایش ایمیل", default=True)
    show_phone = models.BooleanField("نمایش تلفن", default=False)

    views_count = models.PositiveIntegerField(default=0, editable=False)
    downloads_count = models.PositiveIntegerField(default=0, editable=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
        indexes = [
            models.Index(fields=("status", "visibility", "is_listed")),
            models.Index(fields=("slug",)),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.full_name or self.user.username, allow_unicode=True) or self.user.username.lower()
            base = base[:150] or "resume"
            candidate = base
            counter = 2
            while Resume.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{counter}"
                counter += 1
            self.slug = candidate
        if self.visibility != self.Visibility.PUBLIC:
            self.is_listed = False
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("resumes:public", kwargs={"slug": self.slug})

    @property
    def birth_date_display(self):
        return format_jalali_date(self.birth_date, always_show_day=True)

    @property
    def completion_percent(self):
        checks = [
            bool(self.full_name),
            bool(self.job_title),
            bool(self.summary),
            bool(self.email or self.phone),
            self.experiences.exists() or self.educations.exists(),
            self.skills.exists(),
            bool(self.location),
        ]
        return int(sum(checks) / len(checks) * 100)


class OrderedResumeItem(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    position = models.PositiveIntegerField("ترتیب", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ("position", "created_at")

    def save(self, *args, **kwargs):
        if self._state.adding and not self.position:
            current_max = (
                self.__class__.objects.filter(resume=self.resume).aggregate(value=Max("position"))["value"] or 0
            )
            self.position = current_max + 1
        super().save(*args, **kwargs)


class Experience(OrderedResumeItem):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="experiences")
    role = models.CharField("عنوان شغلی", max_length=150)
    company = models.CharField("شرکت / مجموعه", max_length=150)
    location = models.CharField("محل", max_length=120, blank=True)
    start_date = models.CharField("شروع", max_length=10, blank=True)
    end_date = models.CharField("پایان", max_length=10, blank=True)
    is_current = models.BooleanField("هم‌اکنون مشغولم", default=False)
    description = models.TextField("معرفی کوتاه این سابقه", blank=True)
    achievements = models.TextField(
        "وظایف و دستاوردها",
        blank=True,
        help_text="هر وظیفه یا دستاورد را در یک خط جدا بنویس.",
    )

    def save(self, *args, **kwargs):
        if self.is_current:
            self.end_date = ""
        super().save(*args, **kwargs)

    @property
    def start_date_display(self):
        return format_jalali_date(self.start_date)

    @property
    def end_date_display(self):
        return format_jalali_date(self.end_date)

    @property
    def date_range_display(self):
        start = self.start_date_display
        end = "اکنون" if self.is_current else self.end_date_display
        return " تا ".join(value for value in (start, end) if value)

    @property
    def achievement_lines(self):
        return cleaned_lines(self.achievements)

    def __str__(self):
        return f"{self.role} - {self.company}"


class Education(OrderedResumeItem):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="educations")
    degree = models.CharField("مقطع / مدرک", max_length=150)
    field = models.CharField("رشته", max_length=150, blank=True)
    institution = models.CharField("دانشگاه / موسسه", max_length=180)
    location = models.CharField("محل", max_length=120, blank=True)
    start_date = models.CharField("شروع", max_length=10, blank=True)
    end_date = models.CharField("پایان", max_length=10, blank=True)
    is_current = models.BooleanField("هم‌اکنون در حال تحصیل هستم", default=False)
    grade = models.DecimalField(
        "معدل",
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        validators=(MinValueValidator(0), MaxValueValidator(20)),
    )
    description = models.TextField("توضیحات", blank=True)

    def save(self, *args, **kwargs):
        if self.is_current:
            self.end_date = ""
        super().save(*args, **kwargs)

    @property
    def start_date_display(self):
        return format_jalali_date(self.start_date)

    @property
    def end_date_display(self):
        return format_jalali_date(self.end_date)

    @property
    def date_range_display(self):
        start = self.start_date_display
        end = "اکنون" if self.is_current else self.end_date_display
        return " تا ".join(value for value in (start, end) if value)

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Skill(OrderedResumeItem):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "مقدماتی"
        INTERMEDIATE = "intermediate", "متوسط"
        ADVANCED = "advanced", "پیشرفته"
        EXPERT = "expert", "حرفه‌ای"

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField("مهارت", max_length=100)
    category = models.CharField("دسته‌بندی", max_length=100, blank=True)
    level = models.CharField("سطح", max_length=20, choices=Level.choices, default=Level.INTERMEDIATE)
    percentage = models.PositiveSmallIntegerField(
        "درصد نمایشی",
        default=70,
        validators=(MinValueValidator(0), MaxValueValidator(100)),
    )

    def __str__(self):
        return self.name


class SoftSkill(OrderedResumeItem):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="soft_skills")
    name = models.CharField("مهارت نرم", max_length=160)

    def __str__(self):
        return self.name


class Interest(OrderedResumeItem):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="interests")
    name = models.CharField("علاقه‌مندی", max_length=160)

    def __str__(self):
        return self.name


class Language(OrderedResumeItem):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="languages")
    name = models.CharField("زبان", max_length=80)
    level = models.CharField("سطح", max_length=50, blank=True)

    def __str__(self):
        return self.name


class Project(OrderedResumeItem):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField("نام پروژه", max_length=180)
    client = models.CharField("کارفرما / درخواست‌کننده", max_length=150, blank=True)
    project_date = models.CharField("تاریخ پروژه", max_length=10, blank=True)
    description = models.TextField("شرح پروژه و دستاوردها", blank=True)
    tech_stack = models.CharField("فناوری‌ها", max_length=250, blank=True)
    url = models.URLField("لینک دمو", blank=True)
    github_url = models.URLField("لینک کد", blank=True)

    @property
    def project_date_display(self):
        return format_jalali_date(self.project_date)

    @property
    def detail_lines(self):
        return cleaned_lines(self.description)

    def __str__(self):
        return self.title


class Certificate(OrderedResumeItem):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="certificates")
    title = models.CharField("عنوان مدرک", max_length=180)
    issuer = models.CharField("صادرکننده", max_length=150, blank=True)
    issue_date = models.CharField("تاریخ", max_length=10, blank=True)
    credential_url = models.URLField("لینک مدرک", blank=True)
    description = models.TextField("توضیحات", blank=True)

    @property
    def issue_date_display(self):
        return format_jalali_date(self.issue_date)

    def __str__(self):
        return self.title


class SocialLink(OrderedResumeItem):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name="social_links")
    platform = models.CharField("شبکه", max_length=80)
    url = models.URLField("لینک")

    def __str__(self):
        return self.platform
