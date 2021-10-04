#!/usr/bin/env bash

echo "Executing the script!"
sleep 5
echo "Force crond start"
touch /var/log/crawlclima/cron.log
touch /var/log/crawlclima/capture-pegatweets.log
touch /var/log/crawlclima/capture-pegatemperatura.log
service cron restart
echo "Start celery worker"
echo ${pwd}
# To save in file add : --logfile=/var/log/crawlclima/celery-tasks.log
exec celery -A crawlclima.fetchapp worker --concurrency=8 -l INFO
