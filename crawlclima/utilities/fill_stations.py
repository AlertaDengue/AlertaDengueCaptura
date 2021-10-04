import csv
import logging
from os.path import abspath, dirname
from os.path import join as join_path

from crawlclima.models import save

# logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger('fill_stations')

BASE_DIR = dirname(abspath(__file__))
path = join_path(BASE_DIR, 'stations', 'airport_stations_seed.csv')

rows = csv.DictReader(open(path))

try:
    save(rows, schema='Municipio', table='Estacao_wu')
    logger.warning('Import airport code to database successfully!')
except Exception as e:
    logger.warning('The stations are already present in the database!')
