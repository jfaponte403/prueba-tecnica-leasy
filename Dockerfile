FROM python:3.13-slim-bookworm AS build

COPY --from=ghcr.io/astral-sh/uv:0.10.9 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/

RUN DJANGO_DEBUG=false /opt/venv/bin/python src/manage.py collectstatic --noinput

FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings \
    DJANGO_DEBUG=false \
    DJANGO_SQLITE_PATH=/data/db.sqlite3 \
    GUNICORN_WORKERS=2 \
    GUNICORN_THREADS=8

RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --no-create-home --shell /usr/sbin/nologin app \
    && mkdir -p /data \
    && chown app:app /data

WORKDIR /app/src

COPY --from=build /opt/venv /opt/venv
COPY --from=build --chown=app:app /app/src /app/src
COPY --chmod=755 docker/backend-entrypoint.sh /usr/local/bin/entrypoint.sh

USER app

VOLUME ["/data"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/accounts/login/', timeout=2)" || exit 1

ENTRYPOINT ["entrypoint.sh"]
CMD ["sh", "-c", "exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --worker-class gthread --workers ${GUNICORN_WORKERS} --threads ${GUNICORN_THREADS} --access-logfile - --error-logfile -"]
