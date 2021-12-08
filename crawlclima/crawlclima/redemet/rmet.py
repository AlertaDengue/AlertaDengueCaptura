import datetime
import math
import os
import re
import time

import pandas as pd
import psycopg2
import requests
from celery.utils.log import get_task_logger
from dotenv import load_dotenv
from metar.Metar import Metar, ParserError

from crawlclima.config.settings import db_config

load_dotenv()

logger = get_task_logger('redemet')


def get_date_and_standard_metar(raw_data):
    date_str, partially_cleaned_data = raw_data.split(' - ')
    observation_time = datetime.datetime.strptime(date_str, '%Y%m%d%H')
    # The default Metar expects COR modifiers to come after the
    # time data. We will just remove the COR reference and let it
    # be parsed as a regular entry (since it makes no difference
    # for our purposes).
    partially_cleaned_data = partially_cleaned_data.replace('COR ', '')
    cleaned_data = partially_cleaned_data.rstrip('=')
    return observation_time, cleaned_data


def humidity(temperature, dew_point):
    term_a = (17.625 * dew_point) / (243.04 + dew_point)
    term_b = (17.625 * temperature) / (243.04 + temperature)
    return 100 * (math.exp(term_a) / math.exp(term_b))


def clean_line(line):
    if not line:
        return False
    if 'SPECI' in line:
        return False
    if 'não localizada na base de dados da REDEMET' in line:
        return False
    if '////' in line:
        return False
    if len(line.split(' ')) > 22:
        return False
    return True


def parse_page(page):
    lines = filter(clean_line, page.split('\n'))
    records = map(get_date_and_standard_metar, lines)
    data = {
        'observation_time': [],
        'temperature': [],
        'dew_point': [],
        'pressure': [],
        'humidity': [],
    }

    for observation_time, raw_metar in records:
        try:
            m = Metar(raw_metar)
        except ParserError as err:
            logger.error(
                'Error parsing METAR: %s - %s',
                observation_time,
                raw_metar,
                exc_info=True,
            )
            continue
        temperature = m.temp.value()
        dew_point = m.dewpt.value()
        data['observation_time'].append(observation_time)
        data['temperature'].append(temperature)
        data['dew_point'].append(dew_point)
        data['pressure'].append(m.press.value())
        data['humidity'].append(humidity(temperature, dew_point))

    return pd.DataFrame.from_dict(data)


def fahrenheit_to_celsius(f):
    return ((f - 32) / 9.0) * 5


def date_generator(start, end=None):
    delta = (end - start).days if end else 1
    step = delta // abs(delta)
    for days in range(0, delta, step):
        yield start + datetime.timedelta(days)


def redemet_url(station, date):
    api_key = os.getenv('API_KEY')
    url_pattern = (
        'https://api-redemet.decea.gov.br/mensagens/metar/{}?'
        'api_key={}'
        '&data_ini={formatted_date}00&data_fim={formatted_date}23'
    )

    return url_pattern.format(
        station, api_key, formatted_date=date.strftime('%Y%m%d')
    )


def check_day(day, estacao):
    """
    Verifica se dia já foi capturado para uma dada estacao
    :param day: dia (datetime)
    :return: True se ainda não foi capturado ou False, caso contrário.
    """
    sql = 'select data_dia from "Municipio"."Clima_wu" WHERE data_dia=DATE \'{}\' AND "Estacao_wu_estacao_id"=\'{}\''.format(
        day.strftime('%Y-%m-%d'), estacao
    )
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

    field_names = ('temperature', 'humidity', 'pressure')
    aggregations = ('min', 'mean', 'max')

    data = {}
    for field_name in field_names:
        for aggregation in aggregations:
            key = field_name + '_' + aggregation
            try:
                value = summary[field_name].loc[aggregation]
            except KeyError as e:
                value = None
            data[key] = value

    return data


def capture_date_range(station, date_start, date_end=None):
    """
    Baixa dados da estação específica a partir da data especificada até a data de hoje
    :param station: código da estação
    :param date_start: data de início da captura
    :param date_end: data final captura
    :return:
    """
    if date_end is None:
        date_end = datetime.datetime.today()
    check_day_station = lambda d: check_day(d, station)
    dates = filter(check_day_station, date_generator(date_end, date_start))
    return list(filter(len, map(lambda d: capture(station, d), dates)))


def capture(station, date):
    """
    Capture climate data for the given date and station.

    Parameters
    ----------
    station : str
    date : str

    Returns
    -------
    climate_data : dict
        The climate data contains the follow keys: date, station, temperature_{min, mean, max},
        humidity_{min, mean, max} and pressure_{min, mean, max}

    """
    url = redemet_url(station, date)
    status = 0
    wait = 3
    while status != 200 and wait <= 16:
        resp = requests.get(url)
        status = resp.status_code
        time.sleep(wait)
        wait *= 3
    resp_data = resp.json()

    with open('/var/log/crawlclima/capture-pegatemperatura.log', 'w+') as f:
        f.write('{}'.format(resp_data['data']['data']))

    page = ''
    for dados in resp_data['data']['data']:
        mensagem = dados['mens']
        # check if there is more cases that pattern should treat(#53)
        pattern = re.compile(r' [WSNE][0-9]{1,2}/[WSNE][0-9]{1,2}')
        result = pattern.findall(mensagem)
        for r in result:
            mensagem = mensagem.replace(r, '')

        date_receive = dados['recebimento']
        # format date
        date_time_str = datetime.datetime.strptime(
            date_receive, '%Y-%m-%d %H:%M:%S'
        )
        formated_date = date_time_str.strftime('%Y%m%d%H')
        page += '{} - {}\n'.format(formated_date, mensagem)

    dataframe = parse_page(page)
    data = describe(dataframe)

    if len(data) == 0:
        logger.warning('Empty data for %s in %s', station, date)
        return {}

    data['date'] = date
    data['station'] = station

    return data
