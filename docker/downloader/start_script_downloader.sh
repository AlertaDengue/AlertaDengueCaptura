#!/usr/bin/env bash
python docker/downloader/setup.py develop &
exec celery worker -A downloader_app.celeryapp -l info --concurrency=4 &
cron && tail -f /var/log/cron.log

