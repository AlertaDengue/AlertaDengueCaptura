import csv
import os
from multiprocessing.pool import Pool
from os.path import abspath, dirname
from os.path import join as join_path

import psycopg2
from dotenv import load_dotenv
from fill_counties import to_row

load_dotenv()

db_config = {
    "database": os.getenv("PSQL_DB"),
    "user": os.getenv("PSQL_USER"),
    "password": os.getenv("PSQL_PASSWORD"),
    "host": os.getenv("PSQL_HOST"),
    "port": os.getenv("PSQL_PORT"),
}


def to_save(data, schema="Dengue_global", table="Municipio"):
    with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cur:
            for city in data:
                sql = f'''SELECT COUNT(geocodigo) FROM "{schema}"."{table}" WHERE geocodigo={city['county_code']};'''

                cur.execute(sql)
                result = cur.fetchone()

                if len(result) and result[0] == 1:
                    # county_code is stored in the table
                    sql = f'''
                        UPDATE "{schema}"."{table}"
                        SET
                            nome='{city["name"].replace("'", "''")}',
                            geojson='{city["geojson"].replace("'", "''")}',
                            populacao={city["population"]},
                            uf='{city["uf"]}'
                        WHERE
                            geocodigo={city['county_code']}
                    '''
                    cur.execute(sql)
                else:
                    sql = f'''
                        INSERT INTO "{schema}"."{table}"
                        (nome, geocodigo, geojson, populacao, uf)
                        VALUES(
                            '{city["name"].replace("'", "''")}',
                            '{city["geocodigo"]}',
                            '{city["geojson"].replace("'", "''")}',
                            {city["population"]},
                            '{city["uf"]}'
                        )'''

                    cur.execute(sql)


BASE_DIR = dirname(abspath(__file__))
path = join_path(BASE_DIR, "DTB_Only_Municipio_faltantes.csv")
rows = Pool().map(to_row, csv.DictReader(open(path)))
to_save(rows, schema="Dengue_global", table="Municipio")
