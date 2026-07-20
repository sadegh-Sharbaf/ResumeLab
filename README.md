# ResumeLab

پلتفرم رزومه شخصی و رزومه‌ساز چندکاربره با Django.

## امکانات

- ثبت‌نام و ورود با نام کاربری، ایمیل یا شماره تلفن
- چند رزومه برای هر کاربر
- رزومه‌ساز مرحله‌ای: مشخصات فردی، تجربه، تحصیلات، مهارت فنی، مهارت نرم، زبان، علاقه‌مندی، پروژه، مدرک و لینک‌ها
- انتخاب تاریخ‌ها با تقویم شمسی داخلی پروژه
- غیرفعال‌شدن خودکار تاریخ پایان در سابقه شغلی جاری
- ترتیب خودکار تمام آیتم‌ها از ۱ به بعد؛ فیلد ترتیب به کاربر نمایش داده نمی‌شود
- معدل عددی با محدودیت اجباری بین ۰ تا ۲۰
- امکان خالی‌گذاشتن کامل تجربه، تحصیلات، مهارت، زبان، پروژه، مدرک یا لینک
- حذف واقعی فرم‌های داینامیک بدون خطای اعتبارسنجی مورد حذف‌شده
- سه قالب مدرن، مینیمال و کلاسیک با چند رنگ اصلی
- حالت خصوصی، فقط با لینک و عمومی
- نمایش اختیاری رزومه در Explore
- پیش‌نمایش آنلاین و خروجی PDF فارسی/انگلیسی با همان ساختار و تم صفحه وب
- کپی‌کردن رزومه و آمار بازدید/دانلود
- تم تاریک/روشن و رابط واکنش‌گرا
- ابزار قدیمی `/upload/` برای انتقال سریع فایل حفظ شده است

## راه‌اندازی

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

سپس آدرس `http://127.0.0.1:8000/` را باز کنید.

`seed_demo` رزومه نمونه صادق شعرباف را به‌عنوان رزومه ویژه صفحه اصلی ایجاد می‌کند. این کاربر رمز قابل استفاده ندارد؛ برای مدیریت داده‌ها از پنل admin یا حساب مدیر استفاده کنید.

## ارتقا از نسخه قبلی

فقط پس از جایگزینی فایل‌های پروژه اجرا کنید:

```bash
pip install -r requirements.txt
python manage.py migrate
```

Migration جدید تاریخ‌های متنی قدیمی و معدل فارسی را تا جای ممکن به ساختار جدید تبدیل می‌کند.

## تنظیمات محیطی

فایل `.env.example` نمونه متغیرهاست. در Production حداقل موارد زیر را تنظیم کنید:

```text
DJANGO_SECRET_KEY=<long-random-secret>
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
DATABASE_URL=<postgres-connection-url>
```

## استقرار

```bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py seed_demo
gunicorn PersonalWeb.wsgi:application
```

در سرور واقعی فایل‌های media را روی storage پایدار مانند Cloudinary یا S3-compatible storage قرار دهید. WhiteNoise فقط static را سرو می‌کند.

## PDF هم‌شکل صفحه آنلاین و بدون خطای libgobject

PDF از همان HTML و CSS صفحه عمومی رزومه و با **Playwright + Chrome/Edge/Chromium** ساخته می‌شود؛ بنابراین اطلاعات، رنگ، ستون کناری، تصویر، تاریخ‌ها، وظایف و پروژه‌ها در وب و PDF یکسان‌اند. این روش به WeasyPrint، GTK، Pango یا `libgobject` نیاز ندارد.

روی Windows داشتن Google Chrome یا Microsoft Edge کافی است. پروژه مسیر مرورگر را خودکار پیدا می‌کند. در صورت نصب سفارشی، مسیر را در `.env` قرار دهید:

```text
CHROME_BIN=C:\Program Files\Google\Chrome\Application\chrome.exe
```

در Docker/Render، Chromium از طریق `Dockerfile` نصب و `CHROME_BIN=/usr/bin/chromium` تنظیم می‌شود. نصب جداگانه `playwright install` لازم نیست، چون پروژه از مرورگر نصب‌شده سیستم استفاده می‌کند.

## مسیرهای مهم

- `/` صفحه اصلی
- `/dashboard/` داشبورد
- `/resumes/new/` رزومه جدید
- `/explore/` رزومه‌های عمومی
- `/r/<slug>/` صفحه عمومی
- `/r/<slug>/pdf/` دانلود PDF
- `/admin/` مدیریت
- `/upload/` ابزار انتقال سریع فایل

## اجرای تست‌ها

```bash
python manage.py test
```

## استقرار رایگان پیشنهادی

پروژه برای اجرای Docker روی Render آماده شده است. برای جلوگیری از حذف اطلاعات از ترکیب زیر استفاده کنید:

- Render Free Web Service
- Neon PostgreSQL از طریق `DATABASE_URL`
- Cloudinary برای media از طریق `CLOUDINARY_URL`

راهنمای قدم‌به‌قدم فارسی در فایل [`RENDER_DEPLOY_FA.md`](RENDER_DEPLOY_FA.md) قرار دارد. فایل‌های `Dockerfile`، `docker-entrypoint.sh` و `render.yaml` نیز آماده‌اند.
