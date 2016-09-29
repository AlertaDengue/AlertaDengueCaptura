u"""
Created on 29/09/16
by fccoelho
license: GPL V3 or Later
"""

import pandas as pd
import psycopg2
from psycopg2.extras import DictCursor
from decouple import config
import requests
from io import StringIO

db_config = {
    'database': config('POSTGRES_DATABASE'),
    'user': config('POSTGRES_USER'),
    'password': config('POSTGRES_PASSWORD'),
    'host': config('POSTGRES_HOST'),
    'port': config('POSTGRES_PORT'),
}

base_url="http://150.163.255.246:18383/dados_rede"
chave = "bc10602ea62759fab1578f8eb1ff6f7abbf8678d"

def load_station_data(UF="RJ"):
    results = requests.get(base_url, params={'chave': chave,
                                             'inicio': 201412010000,
                                             'fim': 201412010300,
                                             'uf': UF})
    df = pd.read_csv(StringIO(results.text))

