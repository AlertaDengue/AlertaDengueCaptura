#!/usr/bin/env python3

"""
Este script captura series de clima do servidor da Weather Underground em um
período determinado.


Copyright 2014 by Flávio Codeço Coelho
license: GPL v3
"""
import argparse
from datetime import datetime
import time

from crawlclima.wunderground.wu import capture, date_generator, check_day
from utilities.models import save, find_all


rows = find_all(schema='Municipio', table='Estacao_wu')
codes = [row['estacao_id'] for row in rows]
codes.append('all')  # keyword to allow fetching from all stations

date = lambda d: datetime.strptime(d, "%Y-%m-%d")

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--inicio", "-i", type=date, help="Data inicial de captura: yyyy-mm-dd")
parser.add_argument("--fim", "-f", type=date, help="Data final de captura: yyyy-mm-dd")
parser.add_argument("--codigo", "-c", choices=codes, metavar='ICAO', help="Codigo da estação" )
args = parser.parse_args()

station, start, end = args.codigo, args.inicio, args.fim
data = []
i = 0

stations = codes if station == 'all' else [station]
for station in stations:
    if station == 'all':
        continue
    for date in date_generator(start, end):
        if not check_day(date, station):
            print("Date {} has already been captured from station {} ".format(date, station))
            continue
        print("Fetching data from {} at {}.".format(station, date))
        res = capture(station, date)
        print(res)
        data.append(res)
        if i % 10 == 0:
            save(data, schema='Municipio', table='Clima_wu')
            data = []
        time.sleep(1)

save(data, schema='Municipio', table='Clima_wu')
