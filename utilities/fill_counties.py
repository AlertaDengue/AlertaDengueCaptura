import csv
import functools
import os
import time
import warnings
from multiprocessing.pool import Pool
from os.path import abspath, dirname
from os.path import join as join_path

import geojson
import requests
from initials import initials
from models import save


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


@functools.lru_cache(maxsize=None)
def uf_geojson(uf):
    path = os.getenv("GEOJSON_PATH")
    filename = "{}-municipalities.json".format(uf)
    return geojson.load(open(join_path(path, filename), "r"))


def county_polygon(uf, county_code):
    if uf == 0:
        for feature in read_json(county_code)['features']:
            if feature["properties"].get("codarea") == county_code:
                return geojson.dumps(feature)
    else:
        for feature in uf_geojson(uf)["features"]:
            if feature["properties"].get("CD_GEOCODM") == county_code:
                return geojson.dumps(feature)
    warnings.warn("is not in this geojson: {}.".format(county_code))
    return


def to_row(county):
    county_code = county["Cod Municipio Completo"]
    name = county["Nome_Município"]
    uf = county["Nome_UF"]
    try:
        geojson = county_polygon(initials[uf], county_code)
        print(county_code, name, uf)
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


BASE_DIR = dirname(abspath(__file__))
path = join_path(BASE_DIR, "DTB_Only_Municipio_faltantes.csv")
rows = Pool().map(to_row, csv.DictReader(open(path)))
save(rows, schema="Dengue_global", table="Municipio")
