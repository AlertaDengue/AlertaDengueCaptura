import csv
import os
import time
import warnings
from multiprocessing.pool import Pool
from os.path import abspath, dirname
from os.path import join as join_path

import geojson
import psycopg2
import requests
from dotenv import load_dotenv
from initials import initials

load_dotenv()

db_config = {
    "database": os.getenv("PSQL_DB"),
    "user": os.getenv("PSQL_USER"),
    "password": os.getenv("PSQL_PASSWORD"),
    "host": os.getenv("PSQL_HOST"),
    "port": os.getenv("PSQL_PORT"),
}


# Get geojson from geocode
def get_api(geocodigo):
    return f"https://servicodados.ibge.gov.br/api/v3/malhas/municipios/{geocodigo}?formato=application/vnd.geo+json"


# Return data from API
def read_json(geocodigo):
    url = get_api(geocodigo)
    status = 0
    wait = 3
    while status != 200 and wait <= 16:
        resp = requests.get(url)
        status = resp.status_code
        time.sleep(wait)
        wait *= 3
    resp_data = resp.json()
    return resp_data


# Parse data
# Compare cities(Nome_Município) in the csv file
def county_polygon(county_code):
    for feature in read_json(county_code)['features']:
        if feature["properties"].get("codarea") == county_code:
            return geojson.dumps(feature['geometry'])
    warnings.warn("is not in this geojson: {}.".format(county_code))
    return


# Prepare dict to save in the database
def to_row(county):
    county_code = county["Cod Municipio Completo"]
    name = county["Nome_Município"]
    uf = county["Nome_UF"]
    try:
        geojson = county_polygon(county_code)
        print(county_code, "|", name, "|", uf)
    except ValueError as e:
        print(e)
        geojson = ""

    return dict(
        county_code=county_code,
        name=name,
        geojson=geojson,
        uf=initials[uf],
        population=0,
    )


#


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
path = join_path(BASE_DIR, "DTB_2021_Municipio_faltantes.csv")
rows = Pool().map(to_row, csv.DictReader(open(path)))
to_save(rows, schema="Dengue_global", table="Municipio")
