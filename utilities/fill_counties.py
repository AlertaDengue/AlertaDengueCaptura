import csv
import functools
from os.path import abspath, dirname, join as join_path

from decouple import config
import geojson
from multiprocessing.pool import Pool

from initials import initials
from models import save


@functools.lru_cache(maxsize=None)
def uf_geojson(uf):
    path = config('GEOJSON_PATH')
    filename = '{}-municipalities.json'.format(uf)
    return geojson.load(open(join_path(path, filename), "r"))

# TODO: We should improve the complexity of this function
def county_polygon(uf, county_code):
    for feature in uf_geojson(uf)["features"]:
        if feature["properties"].get("CD_GEOCODM") == county_code:
            return geojson.dumps(feature)
    raise ValueError("{} is not in this geojson: {}.".format(county_code, uf))

def to_row(county):
    county_code = county['Cod Municipio Completo']
    name = county['Nome_Município']
    uf = county['Nome_UF']
    try:
        geojson = county_polygon(initials[uf], county_code)
        print(uf, name, county_code)
    except ValueError as e:
        print(e)
        geojson = ''
    return dict(county_code=county_code,
                name=name,
                geojson=geojson,
                uf = initials[uf],
                population=0)

BASE_DIR = dirname(abspath(__file__))
path = join_path(BASE_DIR, "DTB_2014_Municipio.csv")
rows = Pool().map(to_row, csv.DictReader(open(path)))

save(rows, schema="Dengue_global", table="Municipio")
