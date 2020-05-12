#!/usr/bin/env python3
"""
Atualiza tabela de municípios com dados da população estimada
"""
import logging

import pandas as pd
import psycopg2
from decouple import config

logger = logging.getLogger("update-pop")

try:
    conn = psycopg2.connect(
        "dbname='{}' user='{}' host='{}' password='{}'".format(
            config("POSTGRES_DATABASE"),
            config("POSTGRES_USER"),
            config("POSTGRES_HOST"),
            config("POSTGRES_PASSWORD"),
        )
    )
    cur = conn.cursor()
except Exception as e:
    logger.error("Unable to connect to Postgresql: {}".format(e))


df = pd.read_csv("estimativa_pop_municipios_2016.csv.gz", header=0, sep=",")

sql = 'update "Dengue_global"."Municipio" set populacao=%s WHERE geocodigo=%s;'
for i, row in df.iterrows():
    cur.execute(sql, (row.pop_est, row.geocodigo))

conn.commit()
cur.close()
