#!/usr/bin/env python
#coding:utf8
"""
Este script captura series de clima de estações do Rio de Janeiro
a partir do Weather underground

Copyright 2014 by Flávio Codeço Coelho
license: GPL v3
"""
import requests
import re
import pandas as pd
from io import StringIO
import argparse
import datetime
from dateutil.parser import parse
import time

import model_mongo


codes = ['SBRJ',  # santos dumont
         'SBJR',  # Jacarepagua
         'SBGL',  # Galeão
         'IRIODEJA30',  # Cachambi, Meier
         'IRIODEJA14',  # Pepino
         'SBAF',  # Campo dos Afonsos
         'IRIODEJA5',  # Recreio
         'SBCA',  # Cascavel
         ]


def parse_page(page):
    csv = re.subn("<br />", "", page)[0]
    csvf = StringIO(csv)
    df = pd.read_csv(csvf, sep=',', header=0, skiprows=0, parse_dates=True, na_values=["N/A",'-9999'])

    if 'TemperatureF' in df.columns:
        df['TemperatureC'] = fahrenheit_to_celsius(df.TemperatureF)

    return df


def fahrenheit_to_celsius(f):
    """
    Converts temperature from Fahrenheit to Celsius
    """
    return ((f - 32)/9.) * 5


def wu_url_generator(code, start, end=None):
    url_pattern = "http://www.wunderground.com/history/airport/{}/{}/{}/{}/DailyHistory.html?format=1"
    step = datetime.timedelta(1)

    if not end:
        end = start + step
    elif start > end:
        step = -step

    while start != end:
        url = url_pattern.format(code, start.year, start.month, start.day)
        yield url
        start += step


def normalize(station, dataframe):
    summary = dataframe.describe()
    data = {}

    data["date"] = parse(dataframe.DateUTC[0])
    data['station'] = station
    field_names = ('temperature', 'humidity', 'pressure')
    measurements = ('TemperatureC', 'Humidity', 'Sea Level PressurehPa')
    aggregations = ('min', 'mean', 'max')

    for field_name, measurement in zip(field_names, measurements):
        for aggregation in aggregations:
            key = field_name + '_' + aggregation
            value = summary[measurement].ix[aggregation]
            data[key] = value

    return data


def capture(station, start, end, save):
    for url in wu_url_generator(station, start, end):
        print("Fetching data from {}.".format(url))

        page = requests.get(url).text
        df = parse_page(page)
        data = normalize(station, df)
        save(data)

        time.sleep(1)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Pega séries de Clima do servidor da Weather Underground em um período determinado")
    parser.add_argument("--inicio", "-i", help="Data inicial de captura: yyyy-mm-dd")
    parser.add_argument("--fim", "-f", help="Data final de captura: yyyy-mm-dd")
    parser.add_argument("--codigo", "-c", choices=codes, help="Codigo da estação" )
    args = parser.parse_args()
    ini = datetime.datetime.strptime(args.inicio, "%Y-%m-%d")
    fim = datetime.datetime.strptime(args.fim, "%Y-%m-%d")

    capture(args.codigo, ini, fim, model_mongo.save)

