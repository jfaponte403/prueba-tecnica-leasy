#!/bin/sh
set -eu

python manage.py migrate --noinput

if [ "${DJANGO_SEED_DEMO_DATA:-false}" = "true" ]; then
    if ! python manage.py shell -c "from django.contrib.auth.models import User; import sys; sys.exit(0 if User.objects.filter(username='manager').exists() else 1)"; then
        python manage.py seed_assessment_data
    fi
fi

exec "$@"
