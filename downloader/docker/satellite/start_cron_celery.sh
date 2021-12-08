#!/usr/bin/env bash

python docker/satellite/setup.py develop
sleep 10
exec celery -A downloader_app.celeryapp worker -l info --concurrency=4
touch /var/log/cron.log
cron && tail -f /var/log/cron.log
