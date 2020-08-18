#!/usr/bin/env bash
python setup.py develop
exec celery worker -A crawlclima.fetchapp -l info --concurrency=4 &
exec celery worker -A downloader_app.celeryapp -l info &
cron && tail -f /var/log/cron.log

