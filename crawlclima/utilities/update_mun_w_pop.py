#!/usr/bin/env python
"""
Atualiza tabela de municípios com dados da população estimada
"""
import logging
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('update-pop')


try:
    conn = psycopg2.connect(
        "host='{}' port='{}' dbname='{}' user='{}' password='{}'".format(
            os.getenv('PSQL_HOST'),
            os.getenv('PSQL_PORT'),
            os.getenv('PSQL_DB'),
            os.getenv('PSQL_USER'),
            os.getenv('PSQL_PASSWORD'),
        )
    )
    cur = conn.cursor()
except Exception as e:
    logger.error('Unable to connect to Postgresql: {}'.format(e))

df = pd.read_csv(
    'utilities/csv/estimativa_pop_municipios_2020.csv.gz', header=0, sep=','
)


sql = 'UPDATE "Dengue_global"."Municipio" SET populacao=%s WHERE geocodigo=%s;'
for i, row in df.iterrows():
    cur.execute(sql, (row.pop_est, row.geocodigo))

conn.commit()
cur.close()
logger.warning('Update successful in database!')
