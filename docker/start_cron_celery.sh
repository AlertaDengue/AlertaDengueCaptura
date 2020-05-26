#!/usr/bin/env bash
exec celery worker -A crawlclima.fetchapp -l info --concurrency=4 &
cron && tail -f /var/log/cron.log
