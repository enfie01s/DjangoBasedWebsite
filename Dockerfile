# Production image for the Django site: gunicorn on port 8000, static files served by WhiteNoise.
FROM python:3.12-slim AS build
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r /tmp/requirements.txt

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=websitedj.settings
RUN apt-get update \
    && apt-get install -y --no-install-recommends libmariadb3 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

WORKDIR /app
COPY . /app
# Server checkouts are made with umask 077 and COPY keeps those modes; the app runs as a non-root user.
RUN python manage.py collectstatic --noinput \
    && mkdir -p /app/media \
    && chmod -R a+rX /app

EXPOSE 8000
CMD ["gunicorn", "websitedj.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "5", "--timeout", "60", "--access-logfile", "-", "--forwarded-allow-ips", "*"]
