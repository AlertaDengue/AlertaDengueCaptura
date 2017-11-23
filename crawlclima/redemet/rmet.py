from io import StringIO
import datetime
import re
import requests
import pandas as pd
from utilities.models import db_config
import psycopg2
import time


def get_date_and_standard_metar(raw_data):
    date_str, partially_cleaned_data = raw_data.split(' - ')
    observation_time = datetime.datetime.strptime(date_str, '%Y%m%d%H')
    cleaned_data = partially_cleaned_data.rstrip('=')
    return observation_time, cleaned_data


def parse_page(page):
    csv = re.subn("<br />", "", page.strip())[0]
    csvf = StringIO(csv)
    df = pd.read_csv(csvf, sep=',', header=0, parse_dates=True, na_values="N/A")
    df = df.replace(-9999.0, pd.np.nan)
    try:
        if df.ix[0][0] == 'No daily or hourly history data available':
            return pd.DataFrame()
    except IndexError:
        print(page)
        return pd.DataFrame()

    if 'TemperatureF' in df.columns:
        df['TemperatureC'] = fahrenheit_to_celsius(df.TemperatureF)

    return df


def fahrenheit_to_celsius(f):
    return ((f - 32) / 9.) * 5


def date_generator(start, end=None):
    delta = (end - start).days if end else 1
    step = delta // abs(delta)
    for days in range(0, delta, step):
        yield start + datetime.timedelta(days)


def redemet_url(station, date):
    url_pattern = ("https://www.redemet.aer.mil.br/api/consulta_automatica/"
                   "index.php?local={}&msg=metar"
                   "&data_ini={formatted_date}00&data_fim={formatted_date}23")

    return url_pattern.format(station, formatted_date=date.strftime('%Y%m%d'))


def check_day(day, estacao):
    """
    Verifica se dia já foi capturado para uma dada estacao
    :param day: dia (datetime)
    :return: True se ainda não foi capturado ou False, caso contrário.
    """
    sql = 'select data_dia from "Municipio"."Clima_wu" WHERE data_dia=DATE \'{}\' AND "Estacao_wu_estacao_id"=\'{}\''.\
        format(day.strftime("%Y-%m-%d"), estacao)
    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as curr:
            curr.execute(sql)
            rows = curr.fetchall()
    conn.close()  # Context doesn't close connection
    if len(rows) == 0:
        return True
    else:
        return False


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
            try:
                value = summary[measurement].ix[aggregation]
            except KeyError as e:
                value = None
            data[key] = value

    return data


def capture_date_range(station, date):
    """
    Baixa dados da estação específica a partir da data especificada até a data de hoje
    :param station: código da estação
    :param date: data de início da captura
    :return:
    """
    today = datetime.datetime.today()
    check_day_station = lambda d: check_day(d, station)
    dates = filter(check_day_station, date_generator(today, date))
    return list(map(lambda d: capture(station, d), dates))


def capture(station, date):
    url = redemet_url(station, date)
    status = 0
    wait = 1
    while status != 200 and wait <= 16:
        resp = requests.get(url)
        status = resp.status_code
        time.sleep(wait)
        wait *= 2
    print(resp.status_code)
    page = resp.text
    dataframe = parse_page(page)

    data = describe(dataframe)
    data['date'] = date
    data['station'] = station

    return data
