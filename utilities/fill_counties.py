import csv
import functools
import os
import warnings
from multiprocessing.pool import Pool
from os.path import abspath, dirname
from os.path import join as join_path

import geojson
from dotenv import load_dotenv
from initials import initials
from models import save

load_dotenv()


@functools.lru_cache(maxsize=None)
def uf_geojson(uf):
    path = os.getenv("GEOJSON_PATH")
    filename = "{}-municipalities.json".format(uf)
    return geojson.load(open(join_path(path, filename), "r"))


# TODO: We should improve the complexity of this function
def county_polygon(uf: str, county_code: str):
    for feature in uf_geojson(uf)["features"]:
        if feature["properties"].get("CD_GEOCODM") == county_code:
            return geojson.dumps(feature)
    warnings.warn("{} is not in this geojson: {}.".format(county_code, uf))
    return " "


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
path = join_path(BASE_DIR, "DTB_2014_Municipio.csv")
rows = Pool().map(to_row, csv.DictReader(open(path)))
save(rows, schema="Dengue_global", table="Municipio")
