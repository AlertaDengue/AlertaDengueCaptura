#!/usr/bin/env python3
"""
Fetch a week of tweets
Once a week go over the entire year to fill in possible gaps in the local database
requires celery worker to be up and running
but this script will actually be executed by cron
"""
import sys, os
from datetime import datetime, timedelta, date
sys.path.append(os.getcwd())
from crawlclima.tasks import pega_tweets
from itertools import islice


# Data inicial da captura

today = date.fromordinal(date.today().toordinal())
week_ago = date.fromordinal(date.today().toordinal())-timedelta(8)
year_start = date(date.today().year, 1, 1)

with open("municipios") as f:
    municipios = f.read().split('\n')

municipios = list(filter(None, municipios))


def chunk(it, size):
    """
    divide a long list into sizeable chuncks
    :param it: iterable
    :param size: chunk size
    :return:
    """
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())

if today.isoweekday() == 5:
    date_start = year_start
else:
    date_start = week_ago

if len(sys.argv) > 1:
    date_start = sys.argv[1]

for cidades in chunk(municipios, 50):
    pega_tweets.delay(date_start.isoformat(), today.isoformat(), cidades, "A90")
