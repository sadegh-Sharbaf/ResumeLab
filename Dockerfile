FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    CHROME_BIN=/usr/bin/chromium

# Chromium prints the exact same HTML/CSS resume shown on the website.
# This avoids GTK/WeasyPrint dependencies and keeps Persian/RTL rendering stable.
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    fonts-dejavu-core \
    fonts-noto-core \
    libjpeg62-turbo \
    libopenjp2-7 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
RUN chmod +x docker-entrypoint.sh \
    && DJANGO_SECRET_KEY=collectstatic-build-key DJANGO_DEBUG=0 \
       python manage.py collectstatic --noinput

EXPOSE 10000
CMD ["./docker-entrypoint.sh"]
