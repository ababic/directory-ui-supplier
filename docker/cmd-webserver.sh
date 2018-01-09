#!/bin/bash -xe

python /usr/src/app/manage.py collectstatic --noinput
python /usr/src/app/manage.py compilemessages
gunicorn ui.wsgi --bind 0.0.0.0:$PORT --log-file -
