#!/usr/bin/env python3
"""
Atualiza tabela de municípios com dados da população estimada
"""
import pandas as pd
import psycopg2
import logging

logger = logging.getLogger("update-pop")

try:
    conn = psycopg2.connect("dbname='dengue' user='{}' host='{}' password='aldengue'".format('dengueadmin', 'localhost'))
    cur = conn.cursor()
except Exception as e:
    logger.error("Unable to connect to Postgresql: {}".format(e))


df = pd.read_csv("geocodigo_pop_estimada_2014.csv", header=0, sep=',')

sql = 'update "Dengue_global"."Municipio" set populacao=%s WHERE geocodigo=%s;'
for i, row in df.iterrows():
    cur.execute(sql, (row.Pop_estimada, row.Codigo_Municipio))

conn.commit()
cur.close()
