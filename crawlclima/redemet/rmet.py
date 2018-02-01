import datetime
import requests
import pandas as pd
from utilities.models import db_config
import math
import psycopg2
import time

from celery.utils.log import get_task_logger

from metar.Metar import Metar, ParserError


logger = get_task_logger("redemet")


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
            logger.error("Error parsing METAR: %s - %s", observation_time,
                         raw_metar, exc_info=True)
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

    field_names = ('temperature', 'humidity', 'pressure')
    aggregations = ('min', 'mean', 'max')

    data = {}
    for field_name in field_names:
        for aggregation in aggregations:
            key = field_name + '_' + aggregation
            try:
                value = summary[field_name].ix[aggregation]
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
    return list(filter(len, map(lambda d: capture(station, d), dates)))


def capture(station, date):
    url = redemet_url(station, date)
    status = 0
    wait = 1
    while status != 200 and wait <= 16:
        resp = requests.get(url)
        status = resp.status_code
        time.sleep(wait)
        wait *= 2
    page = resp.text
    dataframe = parse_page(page)

    data = describe(dataframe)
    if len(data) == 0:
        logger.warning("Empty data for %s", date)
        return {}
    data['date'] = date
    data['station'] = station

    return data
