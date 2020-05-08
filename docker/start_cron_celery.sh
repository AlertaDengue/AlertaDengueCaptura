#!/usr/bin/env bash
celery worker -A crawlclima.fetchapp -l info --concurrency=4 &
cron && tail -f /var/log/cron.log
