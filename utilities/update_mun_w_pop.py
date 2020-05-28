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

logger = logging.getLogger("update-pop")

try:
    conn = psycopg2.connect(
        "dbname='{}' user='{}' host='{}' password='{}'".format(
            os.getenv("POSTGRES_DATABASE"),
            os.getenv("POSTGRES_USER"),
            os.getenv("POSTGRES_HOST"),
            os.getenv("POSTGRES_PASSWORD"),
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
