#!/usr/bin/env python3
"""
Fetch a week of tweets
Once a week go over the entire year to fill in possible gaps in the local database
requires celery worker to be up and running
but this script will actually be executed by cron
"""

from datetime import datetime, timedelta, date
from crawlclima.tasks import pega_tweets

# Data inicial da captura

today = date.fromordinal(date.today().toordinal())
week_ago = date.fromordinal(date.today().toordinal())-timedelta(8)
year_start = date(date.today().year, 1, 1)

with open("../municipios") as f:
    municipios = f.read().split('\n')


if today.isoweekday() == 5:
    pega_tweets.delay(year_start.isoformat(), today.isoformat(), municipios, "A90")
else:
    pega_tweets.delay(week_ago.isoformat(), today.isoformat(), municipios, "A90")
