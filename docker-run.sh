#!/bin/bash

cd /var/www/maut/maut/
python manage.py migrate --noinput --settings=maut.settings_docker
python manage.py collectstatic --noinput --settings=maut.settings_docker
python manage.py compress --settings=maut.settings_docker
exec gunicorn --env \
  DJANGO_SETTINGS_MODULE=maut.settings_docker \
  maut.wsgi:application -b 0.0.0.0:8000 -w 3 \
  --access-logfile=- --error-logfile=-
