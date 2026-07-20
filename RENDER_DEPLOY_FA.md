# استقرار ResumeLab روی Render با PostgreSQL پایدار

پیکربندی پیشنهادی این پروژه:

- **Render Free Web Service** برای اجرای Django
- **Neon Free PostgreSQL** برای اطلاعات کاربران و رزومه‌ها
- **Cloudinary Free** برای تصاویر آپلودشده
- **WhiteNoise** برای فایل‌های static

> دیتابیس رایگان خود Render بعد از ۳۰ روز منقضی می‌شود؛ برای همین `render.yaml` عمداً دیتابیس Render ایجاد نمی‌کند و مقدار `DATABASE_URL` را از Neon می‌گیرد.

## ۱. ساخت PostgreSQL در Neon

1. در Neon یک پروژه رایگان بساز.
2. از بخش **Connect**، Connection String را کپی کن.
3. رشته باید شبیه این باشد:

```text
postgresql://USER:PASSWORD@HOST/neondb?sslmode=require&channel_binding=require
```

این مقدار را جایی عمومی یا داخل GitHub قرار نده.

## ۲. ساخت فضای تصاویر در Cloudinary

1. یک حساب Cloudinary بساز.
2. از Dashboard مقدار **API Environment variable** را کپی کن.
3. مقدار شبیه این است:

```text
cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

بدون Cloudinary، اطلاعات PostgreSQL باقی می‌ماند ولی تصاویر جدید کاربران روی دیسک موقت Render قرار می‌گیرند و ممکن است با Deploy یا Restart از بین بروند.

## ۳. قراردادن پروژه در GitHub

محتویات پوشه‌ای که `manage.py` و `render.yaml` داخلش هستند را Push کن:

```bash
git init
git add .
git commit -m "Prepare ResumeLab for Render"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

فایل `.env`، دیتابیس محلی و پوشه media نباید Commit شوند.

## ۴. Deploy در Render

روش پیشنهادی:

1. در Render وارد **Blueprints** شو.
2. **New Blueprint Instance** را انتخاب کن.
3. Repository را متصل کن.
4. Render فایل `render.yaml` را تشخیص می‌دهد.
5. برای متغیرهای Secret این مقادیر را وارد کن:

| متغیر | مقدار |
|---|---|
| `DATABASE_URL` | Connection String دریافت‌شده از Neon |
| `CLOUDINARY_URL` | API Environment variable دریافت‌شده از Cloudinary |

`DJANGO_SECRET_KEY` به‌صورت خودکار ساخته می‌شود و دامنه `onrender.com` نیز خودکار به Allowed Hosts و CSRF اضافه می‌شود.

پس از Deploy، Entry Point به‌صورت خودکار این کارها را انجام می‌دهد:

```text
python manage.py migrate
python manage.py seed_demo
Gunicorn start
```

## ۵. ساخت مدیر سایت

از Shell سرویس در Render اجرا کن:

```bash
python manage.py createsuperuser
```

سپس وارد این مسیر شو:

```text
https://YOUR-SERVICE.onrender.com/admin/
```

## ۶. تست سلامت

این مسیر باید JSON با وضعیت `ok` برگرداند:

```text
https://YOUR-SERVICE.onrender.com/healthz/
```

## نکات مهم

- سرویس رایگان Render بعد از بی‌استفاده‌ماندن خاموش می‌شود؛ درخواست بعدی ممکن است با تأخیر باز شود.
- خاموش‌شدن Web Service باعث پاک‌شدن Neon یا Cloudinary نمی‌شود.
- برای محیط واقعی، نسخه پشتیبان دوره‌ای PostgreSQL همچنان توصیه می‌شود.
- `SEED_DEMO=0` رزومه نمونه صفحه اصلی را غیرفعال نمی‌کند، ولی اجرای خودکار فرمان ایجاد/به‌روزرسانی آن را متوقف می‌کند.
- ابزار `/upload/` طبق درخواست پروژه دست‌نخورده مانده است؛ از آن برای ذخیره دائمی فایل روی Render Free استفاده نکن.
