#!/usr/bin/env python3
"""
Fetch a week of data from cemaden
Once a week go over the entire year to fill in possible gaps in the local database
requires celery worker to be up and running
but this script will actually be executed by cron
"""

from datetime import datetime, timedelta, date
from crawlclima.tasks import pega_dados_cemaden, mock

# Data inicial da captura

today = datetime.fromordinal(date.today().toordinal())
week_ago = datetime.fromordinal(date.today().toordinal())-timedelta(8)
year_start = datetime(date.today().year, 1, 1)

if today.isoweekday() != 5:
    pega_dados_cemaden.delay('PR', week_ago, today, 'uf')
    pega_dados_cemaden.delay('RJ', week_ago, today, 'uf')
    pega_dados_cemaden.delay('MG', week_ago, today, 'uf')
else:
    pega_dados_cemaden.delay('PR', year_start, today, 'uf')
    pega_dados_cemaden.delay('RJ', year_start, today, 'uf')
    pega_dados_cemaden.delay('MG', year_start, today, 'uf')

