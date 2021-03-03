import csv
import functools
import logging
import os
from multiprocessing.pool import Pool
from os.path import abspath, dirname
from os.path import join as join_path

import geojson

from utilities.initials import initials
from utilities.models import counties_save


@functools.lru_cache(maxsize=None)
def uf_geojson(uf):
    path = os.getenv("GEOJSON_PATH")
    filename = "{}-municipalities.json".format(uf)
    return geojson.load(open(join_path(path, filename), "r"))


def county_polygon(uf, county_code):
    for feature in uf_geojson(uf)["features"]:
        if feature["properties"].get("code_muni") == int(county_code):
            return geojson.dumps(feature)
    else:
        logging.warning(
            f"{county_code} is not in this geojson {uf}, run get_geosbr.py first..."
        )


def to_row(county):
    county_code = county["Cod Municipio Completo"]
    name = county["Nome_Município"]
    uf = county["Nome_UF"]
    geojson = county_polygon(initials[uf], county_code)
    print(county_code, "|", name, "|", uf)

    return dict(
        county_code=county_code,
        name=name,
        geojson=geojson,
        uf=uf,
        population=0,
    )


BASE_DIR = dirname(abspath(__file__))
path = join_path(BASE_DIR, "DTB_2014_Municipio.csv")
rows = Pool().map(to_row, csv.DictReader(open(path)))
counties_save(rows, schema="Dengue_global", table="Municipio")
