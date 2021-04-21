#!/usr/bin/env bash

echo "Executing the script!"
echo "Installing Python Packages..."
python docker/crawlclima/setup.py develop
sleep 10
echo "Force crond start"
service cron restart
echo "Start celery workert"
exec celery -A crawlclima.fetchapp worker -l info --concurrency=4
