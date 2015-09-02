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

    if df.ix[0][0] == 'No daily or hourly history data available':
        return pd.DataFrame()

    if 'TemperatureF' in df.columns:
        df['TemperatureC'] = fahrenheit_to_celsius(df.TemperatureF)

    return df


def fahrenheit_to_celsius(f):
    """
    Converts temperature from Fahrenheit to Celsius
    """
    return ((f - 32)/9.) * 5


def date_generator(start, end=None):
    delta = (end - start).days if end else 1
    step = delta // abs(delta)
    for days in range(0, delta, step):
        yield start + datetime.timedelta(days)


def wu_url(station, date):
    url_pattern = "http://www.wunderground.com/history/airport/{}/{}/{}/{}/DailyHistory.html?format=1"
    return url_pattern.format(station, date.year, date.month, date.day)

def describe(dataframe):
    if dataframe.empty:
        return {}

    summary = dataframe.describe()

    measurements = ('TemperatureC', 'Humidity', 'Sea Level PressurehPa')
    field_names = ('temperature', 'humidity', 'pressure')
    aggregations = ('min', 'mean', 'max')

    data = {}
    for field_name, measurement in zip(field_names, measurements):
        for aggregation in aggregations:
            key = field_name + '_' + aggregation
            value = summary[measurement].ix[aggregation]
            data[key] = value

    return data


def capture(station, start, end, save):
    for date in date_generator(start, end):
        url = wu_url(station, date)
        print("Fetching data from {}.".format(url))
        page = requests.get(url).text
        dataframe = parse_page(page)

        data = describe(dataframe)
        data['date'] = date
        data['station'] = station

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

