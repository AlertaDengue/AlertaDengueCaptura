import csv
from os.path import abspath, dirname
from os.path import join as join_path

from models import save

BASE_DIR = dirname(abspath(__file__))
path = join_path(BASE_DIR, "stations", "airport_stations_seed.csv")

rows = csv.DictReader(open(path))
save(rows, schema="Municipio", table="Estacao_wu")
