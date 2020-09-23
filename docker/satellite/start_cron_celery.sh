#!/usr/bin/env bash

python docker/satellite/setup.py develop &
exec celery worker -A downloader_app.celeryapp -l info --concurrency=4 &
touch /var/log/cron.log &
cron && tail -f /var/log/cron.log
