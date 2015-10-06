#!/usr/bin/env python3
"""
Fetch a week of data from cemaden
"""

from datetime import datetime, timedelta, date
from crawlclima.tasks import pega_dados_cemaden, mock

# Data inicial da captura

today = datetime.fromordinal(date.today().toordinal())
week_ago = datetime.fromordinal(date.today().toordinal())-timedelta(8)

pega_dados_cemaden.delay('PR', week_ago, today, 'uf')
pega_dados_cemaden.delay('RJ', week_ago, today, 'uf')
pega_dados_cemaden.delay('MG', week_ago, today, 'uf')

