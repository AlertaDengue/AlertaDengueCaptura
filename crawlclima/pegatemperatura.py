#!/usr/bin/env python3
"""
Este script deve ser executado via cron, diariamente para
lançar a tarefa de captura de dados de temperatura do Weather underground
veja crontab para saber como executar este script
"""
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.getcwd())

from crawlclima.tasks import fetch_redemet
from utilities.models import find_all


user_date = None
if len(sys.argv) > 1:
    user_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")

today = datetime.today() if user_date is None else user_date
year_start = datetime(datetime.today().year, 1, 1)

yesterday = today - timedelta(1)

rows = find_all(schema='Municipio', table='Estacao_wu')
stations = [row['estacao_id'] for row in rows]


day = year_start if today.isoweekday() == 5 else yesterday

for station in stations:
    fetch_redemet.delay(station, day)
