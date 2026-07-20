from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from accounts.models import Profile, User
from resumes.models import (
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


class Command(BaseCommand):
    help = "Create or refresh the complete featured Sadegh Sharbaf resume used on the landing page."

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username="sadegh",
            defaults={
                "email": "mohammadsadeghsherbaf@gmail.com",
                "phone": "+989379149904",
                "first_name": "صادق",
                "last_name": "شعرباف",
                "is_active": True,
            },
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=("password",))
        Profile.objects.get_or_create(user=user, defaults={"city": "اصفهان"})

        Resume.objects.filter(is_featured=True).exclude(user=user).update(is_featured=False)
        resume, _ = Resume.objects.update_or_create(
            user=user,
            slug="sadegh-sharbaf",
            defaults={
                "title": "رزومه کامل برنامه‌نویس بک‌اند",
                "full_name": "صادق شعرباف",
                "job_title": "برنامه‌نویس بک‌اند وب",
                "summary": (
                    "برنامه‌نویس Backend با تمرکز بر Django، Python و Django REST Framework و تجربه در طراحی و "
                    "توسعه RESTful API. دارای تجربه پیاده‌سازی احراز هویت، مدیریت سطوح دسترسی، مدل‌سازی داده و "
                    "توسعه پروژه‌های مبتنی بر Django. آشنا با Git، Redis، Celery، PostgreSQL و مفاهیم ارتباطات "
                    "Real-Time با Django Channels. علاقه‌مند به یادگیری مستمر، حل مسئله، توسعه نرم‌افزارهای "
                    "باکیفیت و کار تیمی."
                ),
                "birth_date": "1379/11/06",
                "marital_status": Resume.MaritalStatus.SINGLE,
                "military_status": Resume.MilitaryStatus.COMPLETED,
                "email": "mohammadsadeghsherbaf@gmail.com",
                "phone": "+989379149904",
                "alternate_phone": "09334836995",
                "location": "اصفهان",
                "website": "https://github.com/SadeghSharbaf",
                "language": Resume.Language.FA,
                "template": Resume.Template.MODERN,
                "accent_color": "#8b5cf6",
                "status": Resume.Status.PUBLISHED,
                "visibility": Resume.Visibility.PUBLIC,
                "is_listed": True,
                "is_featured": True,
                "show_email": True,
                "show_phone": True,
            },
        )

        avatar_path = settings.BASE_DIR / "base" / "static" / "img" / "sadegh.jpg"
        if avatar_path.exists() and not resume.avatar:
            with avatar_path.open("rb") as image:
                resume.avatar.save("sadegh.jpg", File(image), save=True)

        for manager in (
            resume.experiences,
            resume.educations,
            resume.skills,
            resume.soft_skills,
            resume.interests,
            resume.languages,
            resume.projects,
            resume.certificates,
            resume.social_links,
        ):
            manager.all().delete()

        Experience.objects.bulk_create(
            [
                Experience(
                    resume=resume,
                    position=1,
                    role="طراح و برنامه‌نویس ارشد",
                    company="زیروتیم",
                    location="اصفهان",
                    start_date="1405/03/01",
                    is_current=True,
                    achievements=(
                        "طراحی و توسعه سیستم‌های Backend: پیاده‌سازی و توسعه سرویس‌های سمت سرور با استفاده از Django و Django REST Framework برای پروژه‌های وب، اپلیکیشن و ربات‌های پیام‌رسان تلگرام و بله.\n"
                        "مدیریت و طراحی APIهای کارآمد و امن: ایجاد RESTful APIهای مقیاس‌پذیر، مستند و ایمن برای ارتباط یکپارچه بین فرانت‌اند، اپلیکیشن‌های موبایل و ربات‌های پیام‌رسان.\n"
                        "پیاده‌سازی تسک‌های آسنکرون و پس‌زمینه با Celery و Redis برای مدیریت تسک‌های زمان‌بر مانند ارسال ایمیل، پردازش داده و تولید گزارش.\n"
                        "اتصال پروژه‌ها به سرویس‌های شخص ثالث مانند SendGrid، درگاه‌های پرداخت و APIهای مختلف.\n"
                        "استفاده از Git و پلتفرم‌هایی مانند GitLab و GitHub برای هماهنگی تیمی و مدیریت چرخه توسعه نرم‌افزار و CI/CD.\n"
                        "طراحی معماری و رعایت اصول Clean Code، SOLID و DRY برای نگهداری و توسعه آسان پروژه‌ها."
                    ),
                ),
                Experience(
                    resume=resume,
                    position=2,
                    role="برنامه‌نویس بک‌اند وب",
                    company="پروژه‌های منتورمحور و شخصی",
                    location="اصفهان",
                    start_date="1403/08/01",
                    is_current=True,
                    achievements=(
                        "سرتیم بک‌اند زیروتیم.\n"
                        "طراحی و پیاده‌سازی بیش از ۱۰ پروژه شخصی و آموزشی مبتنی بر Django و Django REST Framework با معماری RESTful API.\n"
                        "توسعه ماژول‌های احراز هویت، مدیریت کاربران، سطوح دسترسی و Permissionهای سفارشی در پروژه‌های مختلف.\n"
                        "طراحی و پیاده‌سازی سیستم‌های CRUD، مدل‌سازی پایگاه داده و مدیریت منطق کسب‌وکار در پروژه‌هایی مانند سامانه کتابخانه، انبارداری و مدیریت فیلم.\n"
                        "پیاده‌سازی و تست APIها با Postman و رفع خطاهای مرتبط با توسعه و یکپارچه‌سازی سرویس‌ها.\n"
                        "استفاده از Git در مدیریت نسخه و همکاری تیمی در فرایند توسعه نرم‌افزار.\n"
                        "پیاده‌سازی تسک‌های پس‌زمینه با Redis و Celery در پروژه‌های آموزشی.\n"
                        "استفاده از PostgreSQL به‌عنوان پایگاه داده در پروژه‌های Django.\n"
                        "اتصال پروژه‌ها به سرویس‌های خارجی مانند SendGrid برای ارسال ایمیل.\n"
                        "توسعه قابلیت‌های Real-Time و WebSocket با Django Channels.\n"
                        "رعایت اصول Clean Code، OOP و ساختاردهی مناسب پروژه‌های بک‌اند.\n"
                        "آشنایی مقدماتی و انجام یک پروژه تمرینی با FastAPI."
                    ),
                ),
                Experience(
                    resume=resume,
                    position=3,
                    role="همکار تولید",
                    company="شرکت دیجیتال آلارم",
                    location="اصفهان",
                    start_date="1398/07/01",
                    end_date="1405/04/01",
                    is_current=False,
                    achievements=(
                        "مونتاژ بردهای الکترونیکی دزدگیر اماکن با دقت بالا.\n"
                        "کار با ابزارهای لحیم‌کاری، تست و کنترل کیفیت قطعات.\n"
                        "تجزیه و تحلیل داده‌های عملکرد پروژه‌ها و ارائه پیشنهادهای بهینه‌سازی که منجر به کاهش ۱۰ درصدی هزینه‌ها شد.\n"
                        "همکاری در تیم تولید برای تضمین عملکرد صحیح مدارها.\n"
                        "آشنایی با عملکرد کلی سیستم‌های امنیتی و مدارهای دیجیتال."
                    ),
                ),
            ]
        )

        Education.objects.create(
            resume=resume,
            position=1,
            degree="کارشناسی مهندسی کامپیوتر",
            field="برنامه‌نویسی وب",
            institution="دانشگاه آزاد اسلامی خوراسگان",
            location="اصفهان",
            start_date="1403/07/01",
            is_current=True,
            grade="18.63",
        )

        skill_names = [
            ("Python", "Programming", "advanced", 88),
            ("Django", "Backend", "advanced", 86),
            ("Django REST Framework", "Backend", "advanced", 84),
            ("OOP", "Programming", "advanced", 82),
            ("RESTful API Design", "Backend", "advanced", 80),
            ("Postman", "Tools", "advanced", 80),
            ("Git", "Tools", "advanced", 78),
            ("Redis", "Backend", "intermediate", 66),
            ("Celery", "Backend", "intermediate", 64),
            ("Django Channels", "Backend", "intermediate", 60),
            ("PostgreSQL", "Database", "intermediate", 68),
            ("SQLite", "Database", "intermediate", 70),
            ("Data Structures & Algorithms", "Computer Science", "intermediate", 64),
            ("HTTP & Web Fundamentals", "Web", "intermediate", 72),
            ("C#", "Programming", "beginner", 42),
            ("Docker", "DevOps", "intermediate", 62),
        ]
        Skill.objects.bulk_create(
            [
                Skill(
                    resume=resume,
                    position=index,
                    name=name,
                    category=category,
                    level=level,
                    percentage=percentage,
                )
                for index, (name, category, level, percentage) in enumerate(skill_names, start=1)
            ]
        )

        Language.objects.bulk_create(
            [
                Language(resume=resume, position=1, name="انگلیسی", level="B2"),
                Language(resume=resume, position=2, name="آلمانی", level="A1"),
            ]
        )

        soft_skills = [
            "توانایی یادگیری سریع و خودآموزی",
            "مدیریت زمان و مسئولیت‌پذیری",
            "علاقه‌مند به کار تیمی و همکاری",
            "دقت، حل مسئله و انعطاف‌پذیری",
            "شنونده خوب",
            "خلاقیت و ایده‌پردازی",
            "انتقادپذیری، اعتمادبه‌نفس و پشتکار",
            "قدرت تأثیرگذاری بر دیگران",
        ]
        SoftSkill.objects.bulk_create(
            [SoftSkill(resume=resume, position=index, name=name) for index, name in enumerate(soft_skills, start=1)]
        )

        interests = ["ریاضیات", "الگوریتم‌های برنامه‌نویسی", "موسیقی", "فلسفه"]
        Interest.objects.bulk_create(
            [Interest(resume=resume, position=index, name=name) for index, name in enumerate(interests, start=1)]
        )

        Project.objects.bulk_create(
            [
                Project(
                    resume=resume,
                    position=1,
                    title="سامانه امانت‌داری کتابخانه",
                    client="شخصی",
                    project_date="1403/09/01",
                    tech_stack="Django, Celery, SendGrid, Custom User, Middleware",
                    description=(
                        "توسعه سامانه تحت وب برای مدیریت کتاب‌ها، کاربران و فرایند امانت و بازگشت کتاب.\n"
                        "پیاده‌سازی سیستم احراز هویت و مدیریت دسترسی کاربران با Custom User Model.\n"
                        "توسعه Middleware سفارشی برای محدودسازی دسترسی کاربران به بخش‌های مختلف سامانه.\n"
                        "پیاده‌سازی منطق امانت کتاب و کنترل وضعیت موجود بودن کتاب‌ها.\n"
                        "استفاده از Celery برای وظایف زمان‌بندی‌شده و ارسال اعلان ایمیلی به کاربران دارای تأخیر در بازگرداندن کتاب.\n"
                        "طراحی مدل‌های داده و روابط بین کاربران، کتاب‌ها و سوابق امانت.\n"
                        "استفاده از Class-Based Views و قابلیت‌های Django برای توسعه و نگهداری بهتر پروژه."
                    ),
                    github_url="https://github.com/SadeghSharbaf/Library",
                ),
                Project(
                    resume=resume,
                    position=2,
                    title="سامانه مدیریت انبارداری",
                    client="شخصی",
                    project_date="1404/01/01",
                    tech_stack="Django REST Framework, PostgreSQL, ViewSets, Serializers",
                    description=(
                        "طراحی و توسعه RESTful API برای مدیریت کالاها، خریدها و موجودی انبار با Django REST Framework.\n"
                        "پیاده‌سازی سیستم ثبت ورود و خروج کالا و به‌روزرسانی خودکار موجودی انبار.\n"
                        "توسعه منطق کنترل موجودی و اعتبارسنجی عملیات برای جلوگیری از ثبت خروج بیش از موجودی.\n"
                        "پیاده‌سازی تاریخچه تغییرات موجودی و Audit Log عملیات کاربران.\n"
                        "طراحی مدل‌های داده و روابط بین کالا، خرید، موجودی و تراکنش‌های انبار.\n"
                        "استفاده از ViewSets، Generic Views و Serializerهای سفارشی برای توسعه API.\n"
                        "پیاده‌سازی فیلترگذاری داده‌ها و مدیریت دسترسی کاربران احراز هویت‌شده.\n"
                        "تست و اعتبارسنجی APIها با Postman."
                    ),
                    github_url="https://github.com/SadeghSharbaf/warehouse",
                ),
                Project(
                    resume=resume,
                    position=3,
                    title="سامانه اختصاصی حضور و غیاب",
                    client="زیروتیم",
                    project_date="1405/02/01",
                    tech_stack="Django, Django REST Framework, RESTful API",
                    description=(
                        "طراحی و پیاده‌سازی یک سیستم Backend کامل و امن برای ثبت، مدیریت و گزارش‌گیری حضور و غیاب کارکنان سازمان‌ها.\n"
                        "جایگزینی روش‌های سنتی دست‌نویس یا کارت‌زنی با APIهای قدرتمند.\n"
                        "فراهم‌کردن امکان اتصال به اپلیکیشن موبایل، پنل مدیریتی وب و ربات‌های پیام‌رسان."
                    ),
                ),
                Project(
                    resume=resume,
                    position=4,
                    title="برنامه ویندوز مدیریت حسابداری",
                    client="دانشگاه",
                    project_date="1403/10/01",
                    tech_stack="C#, Windows Desktop",
                    description="پروژه دانشگاهی برای مدیریت و حسابداری.",
                    github_url="https://github.com/SadeghSharbaf/Cost_management",
                ),
            ]
        )

        Certificate.objects.bulk_create(
            [
                Certificate(
                    resume=resume,
                    position=1,
                    title="مدرک مهارت برنامه‌نویسی پایتون",
                    issuer="کوئرا",
                    issue_date="1403/06/01",
                    credential_url="https://quera.org/media/public/certificate/c6643e3906244a89a07433395e542d43.png",
                ),
                Certificate(
                    resume=resume,
                    position=2,
                    title="گواهینامه طراحی و توسعه وب‌اپلیکیشن‌های بک‌اند",
                    issue_date="1403/01/01",
                ),
            ]
        )

        SocialLink.objects.bulk_create(
            [
                SocialLink(resume=resume, position=1, platform="GitHub", url="https://github.com/SadeghSharbaf"),
                SocialLink(
                    resume=resume,
                    position=2,
                    platform="LinkedIn",
                    url="https://linkedin.com/in/sadegh-sherbaf-069b18384",
                ),
                SocialLink(resume=resume, position=3, platform="Telegram", url="https://t.me/M_S_Sharbaf"),
            ]
        )
        self.stdout.write(self.style.SUCCESS(f"Featured resume ready: {resume.get_absolute_url()}"))
