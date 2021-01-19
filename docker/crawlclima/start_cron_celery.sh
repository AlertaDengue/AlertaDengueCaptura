#!/usr/bin/env bash

python docker/crawlclima/setup.py develop
sleep 10
exec celery -A crawlclima.fetchapp worker -l info --concurrency=4
cron && tail -f /var/log/cron.log
