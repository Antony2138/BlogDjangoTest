#!/bin/sh

set -e
python3 manage.py migrate --no-input
python3 manage.py collectstatic --no-input
daphne -b 0.0.0.0 -p 8000 testBlog.asgi:application
exec "$@"
