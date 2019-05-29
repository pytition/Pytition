#!/usr/bin/env sh
set -e

# we collect the static
python3 pytition/manage.py collectstatic

# wait for postgres to start
while ! nc -z db 5432; do echo "waiting for postgres to start..." && sleep 1; done;

# and initialize the db, ignore the errors
python3 pytition/manage.py migrate

# we call the base image entry point (that will start nginx/uwsgi)
echo "starting pytition"
exec /entrypoint.sh "/usr/bin/supervisord"
