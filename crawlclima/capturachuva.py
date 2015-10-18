#!/usr/bin/env python3
"""
Fetch a week of data from cemaden
Once a week go over the entire year to fill in possible gaps in the local database
requires celery worker to be up and running
but this script will actually be executed by cron
"""
import os, sys
from datetime import datetime, timedelta, date
sys.path.append(os.getcwd())
from crawlclima.tasks import pega_dados_cemaden, mock

# Data inicial da captura

today = datetime.fromordinal(date.today().toordinal())
week_ago = datetime.fromordinal(date.today().toordinal())-timedelta(8)
year_start = datetime(date.today().year, 1, 1)

date_from = week_ago if today.isoweekday() != 5 else year_start


pega_dados_cemaden.delay('PR', date_from, today, 'uf')
pega_dados_cemaden.delay('RJ', date_from, today, 'uf')
pega_dados_cemaden.delay('MG', date_from, today, 'uf')


