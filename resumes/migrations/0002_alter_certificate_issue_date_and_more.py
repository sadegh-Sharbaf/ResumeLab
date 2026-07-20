# Generated for ResumeLab: Jalali date normalization and numeric grade validation.

import re

import django.core.validators
from django.db import migrations, models


DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
MONTHS = {
    "فروردین": 1,
    "اردیبهشت": 2,
    "خرداد": 3,
    "تیر": 4,
    "مرداد": 5,
    "شهریور": 6,
    "مهر": 7,
    "آبان": 8,
    "آذر": 9,
    "دی": 10,
    "بهمن": 11,
    "اسفند": 12,
}


def normalize_date(value):
    text = str(value or "").translate(DIGITS).strip()
    if not text or text in {"اکنون", "هم اکنون", "هم‌اکنون"}:
        return ""
    match = re.fullmatch(r"(\d{4})[/-](\d{1,2})(?:[/-](\d{1,2}))?", text)
    if match:
        year, month, day = match.groups()
        return f"{int(year):04d}/{int(month):02d}/{int(day or 1):02d}"
    match = re.fullmatch(r"([آ-ی]+)\s+(\d{4})", text)
    if match and match.group(1) in MONTHS:
        return f"{int(match.group(2)):04d}/{MONTHS[match.group(1)]:02d}/01"
    if re.fullmatch(r"\d{4}", text):
        return f"{int(text):04d}/01/01"
    return ""


def normalize_legacy_values(apps, schema_editor):
    Education = apps.get_model("resumes", "Education")
    Experience = apps.get_model("resumes", "Experience")
    Certificate = apps.get_model("resumes", "Certificate")

    for item in Experience.objects.all().iterator():
        item.start_date = normalize_date(item.start_date)
        item.end_date = "" if item.is_current else normalize_date(item.end_date)
        item.save(update_fields=["start_date", "end_date"])

    for item in Education.objects.all().iterator():
        item.start_date = normalize_date(item.start_date)
        item.end_date = normalize_date(item.end_date)
        grade = str(item.grade or "").translate(DIGITS).replace("٫", ".").strip()
        try:
            numeric = float(grade) if grade else None
        except (TypeError, ValueError):
            numeric = None
        item.grade = str(numeric) if numeric is not None and 0 <= numeric <= 20 else None
        item.save(update_fields=["start_date", "end_date", "grade"])

    for item in Certificate.objects.all().iterator():
        item.issue_date = normalize_date(item.issue_date)
        item.save(update_fields=["issue_date"])


class Migration(migrations.Migration):

    dependencies = [
        ("resumes", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="education",
            name="grade",
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name="معدل"),
        ),
        migrations.RunPython(normalize_legacy_values, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="certificate",
            name="issue_date",
            field=models.CharField(blank=True, max_length=10, verbose_name="تاریخ"),
        ),
        migrations.AlterField(
            model_name="education",
            name="end_date",
            field=models.CharField(blank=True, max_length=10, verbose_name="پایان"),
        ),
        migrations.AlterField(
            model_name="education",
            name="grade",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=4,
                null=True,
                validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(20)],
                verbose_name="معدل",
            ),
        ),
        migrations.AlterField(
            model_name="education",
            name="start_date",
            field=models.CharField(blank=True, max_length=10, verbose_name="شروع"),
        ),
        migrations.AlterField(
            model_name="experience",
            name="end_date",
            field=models.CharField(blank=True, max_length=10, verbose_name="پایان"),
        ),
        migrations.AlterField(
            model_name="experience",
            name="start_date",
            field=models.CharField(blank=True, max_length=10, verbose_name="شروع"),
        ),
    ]
