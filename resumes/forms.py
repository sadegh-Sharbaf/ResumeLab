import re
from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import Certificate, Education, Experience, Interest, Language, Project, Resume, Skill, SoftSkill, SocialLink


PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_number(value):
    return str(value or "").translate(PERSIAN_DIGITS).replace("٫", ".").replace("٬", "").strip()


def is_jalali_leap(year):
    epbase = year - (474 if year >= 0 else 473)
    epyear = 474 + (epbase % 2820)
    return ((epyear + 38) * 682) % 2816 < 682


class PersianDecimalField(forms.DecimalField):
    def to_python(self, value):
        return super().to_python(normalize_number(value))


class JalaliDateField(forms.CharField):
    default_error_messages = {
        "invalid": "تاریخ را از تقویم شمسی و با قالب ۱۴۰۳/۰۵/۲۱ انتخاب کن.",
    }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        kwargs.setdefault(
            "widget",
            forms.TextInput(
                attrs={
                    "class": "form-control jalali-date-input",
                    "placeholder": "انتخاب از تقویم شمسی",
                    "autocomplete": "off",
                    "readonly": "readonly",
                    "inputmode": "none",
                    "data-jalali-date": "1",
                }
            ),
        )
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)
        if not value:
            return ""
        value = normalize_number(value).replace("-", "/")
        match = re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", value)
        if not match:
            raise ValidationError(self.error_messages["invalid"], code="invalid")
        year, month, day = map(int, match.groups())
        if not 1200 <= year <= 1600 or not 1 <= month <= 12:
            raise ValidationError(self.error_messages["invalid"], code="invalid")
        max_day = 31 if month <= 6 else 30 if month <= 11 else (30 if is_jalali_leap(year) else 29)
        if not 1 <= day <= max_day:
            raise ValidationError(self.error_messages["invalid"], code="invalid")
        return f"{year:04d}/{month:02d}/{day:02d}"


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check")
            elif isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.setdefault("class", "choice-list")
            else:
                current = field.widget.attrs.get("class", "")
                if "form-control" not in current:
                    field.widget.attrs["class"] = f"{current} form-control".strip()


class ResumeBasicForm(StyledModelForm):
    birth_date = JalaliDateField(label="تاریخ تولد")

    class Meta:
        model = Resume
        fields = (
            "title",
            "full_name",
            "job_title",
            "summary",
            "birth_date",
            "marital_status",
            "military_status",
            "email",
            "phone",
            "alternate_phone",
            "location",
            "website",
            "avatar",
            "show_email",
            "show_phone",
            "language",
        )
        widgets = {"summary": forms.Textarea(attrs={"rows": 6})}


class ResumeDesignForm(StyledModelForm):
    class Meta:
        model = Resume
        fields = ("template", "accent_color", "status", "visibility", "is_listed", "slug")
        widgets = {
            "template": forms.RadioSelect,
            "accent_color": forms.RadioSelect,
            "status": forms.RadioSelect,
            "visibility": forms.RadioSelect,
        }
        help_texts = {
            "slug": "بخش انتهایی لینک عمومی؛ حروف فارسی هم پشتیبانی می‌شود.",
            "is_listed": "فقط رزومه عمومی و منتشرشده در Explore نمایش داده می‌شود.",
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("visibility") != Resume.Visibility.PUBLIC:
            cleaned["is_listed"] = False
        if cleaned.get("is_listed") and cleaned.get("status") != Resume.Status.PUBLISHED:
            self.add_error("is_listed", "برای نمایش در Explore، وضعیت را منتشرشده قرار بده.")
        return cleaned


class ExperienceForm(StyledModelForm):
    start_date = JalaliDateField(label="تاریخ شروع")
    end_date = JalaliDateField(label="تاریخ پایان")

    class Meta:
        model = Experience
        fields = ("role", "company", "location", "start_date", "end_date", "is_current", "description", "achievements")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "achievements": forms.Textarea(attrs={"rows": 8, "placeholder": "هر وظیفه یا دستاورد را در یک خط جدا بنویس"}),
            "is_current": forms.CheckboxInput(attrs={"data-current-toggle": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["end_date"].widget.attrs["data-end-date"] = "1"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("is_current"):
            cleaned["end_date"] = ""
        return cleaned


class EducationForm(StyledModelForm):
    start_date = JalaliDateField(label="تاریخ شروع")
    end_date = JalaliDateField(label="تاریخ پایان")
    grade = PersianDecimalField(
        label="معدل",
        required=False,
        min_value=Decimal("0"),
        max_value=Decimal("20"),
        max_digits=4,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"min": "0", "max": "20", "step": "0.01", "inputmode": "decimal"}),
        error_messages={
            "min_value": "معدل نمی‌تواند کمتر از ۰ باشد.",
            "max_value": "معدل باید حداکثر ۲۰ باشد.",
            "invalid": "معدل را به‌صورت عددی بین ۰ تا ۲۰ وارد کن.",
        },
    )

    class Meta:
        model = Education
        fields = ("degree", "field", "institution", "location", "start_date", "end_date", "is_current", "grade", "description")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "is_current": forms.CheckboxInput(attrs={"data-current-toggle": "1"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["end_date"].widget.attrs["data-end-date"] = "1"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("is_current"):
            cleaned["end_date"] = ""
        return cleaned

    def clean_grade(self):
        value = self.cleaned_data.get("grade")
        return value


class SkillForm(StyledModelForm):
    class Meta:
        model = Skill
        fields = ("name", "category", "level", "percentage")


class SoftSkillForm(StyledModelForm):
    class Meta:
        model = SoftSkill
        fields = ("name",)


class InterestForm(StyledModelForm):
    class Meta:
        model = Interest
        fields = ("name",)


class LanguageForm(StyledModelForm):
    class Meta:
        model = Language
        fields = ("name", "level")


class ProjectForm(StyledModelForm):
    project_date = JalaliDateField(label="تاریخ پروژه")

    class Meta:
        model = Project
        fields = ("title", "client", "project_date", "description", "tech_stack", "url", "github_url")
        widgets = {"description": forms.Textarea(attrs={"rows": 8, "placeholder": "شرح پروژه یا هر دستاورد را در یک خط جدا بنویس"})}


class CertificateForm(StyledModelForm):
    issue_date = JalaliDateField(label="تاریخ صدور")

    class Meta:
        model = Certificate
        fields = ("title", "issuer", "issue_date", "credential_url", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class SocialLinkForm(StyledModelForm):
    class Meta:
        model = SocialLink
        fields = ("platform", "url")


FORMSET_OPTIONS = {
    "extra": 0,
    "can_delete": True,
    "min_num": 0,
    "validate_min": False,
}

ExperienceFormSet = inlineformset_factory(Resume, Experience, form=ExperienceForm, **FORMSET_OPTIONS)
EducationFormSet = inlineformset_factory(Resume, Education, form=EducationForm, **FORMSET_OPTIONS)
SkillFormSet = inlineformset_factory(Resume, Skill, form=SkillForm, **FORMSET_OPTIONS)
SoftSkillFormSet = inlineformset_factory(Resume, SoftSkill, form=SoftSkillForm, **FORMSET_OPTIONS)
InterestFormSet = inlineformset_factory(Resume, Interest, form=InterestForm, **FORMSET_OPTIONS)
LanguageFormSet = inlineformset_factory(Resume, Language, form=LanguageForm, **FORMSET_OPTIONS)
ProjectFormSet = inlineformset_factory(Resume, Project, form=ProjectForm, **FORMSET_OPTIONS)
CertificateFormSet = inlineformset_factory(Resume, Certificate, form=CertificateForm, **FORMSET_OPTIONS)
SocialLinkFormSet = inlineformset_factory(Resume, SocialLink, form=SocialLinkForm, **FORMSET_OPTIONS)
