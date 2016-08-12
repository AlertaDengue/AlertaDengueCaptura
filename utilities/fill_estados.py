#!/usr/bin/env python3
import psycopg2
from decouple import config
import glob
import os
import geojson

db_config = {
    'database': config('POSTGRES_DATABASE'),
    'user': config('POSTGRES_USER'),
    'password': config('POSTGRES_PASSWORD'),
    'host': config('POSTGRES_HOST'),
    'port': config('POSTGRES_PORT'),
}

path = config('GEOJSON_PATH')

def load_geojson(fname):
    with open(fname,'r') as f:
        return geojson.load(f)


if __name__=="__main__":
    conn = psycopg2.connect(**db_config)
    with conn.cursor() as cur:
        for fname in glob.glob(os.path.join(path, '*-state.json')):
            print("Processing {}".format(fname))
            geo_json = load_geojson(fname)
            properties = geo_json['features'][0]['properties']
            nome = properties['NM_ESTADO']
            geocodigo = properties['CD_GEOCODU']
            regiao = properties['NM_REGIAO']
            cur.execute('insert into "Dengue_global".estado (uf, nome, regiao, geocodigo, geojson) values(%s,%s,%s,%s, %s)',
                        (uf, nome, regiao, geocodigo, geojson.dumps(geo_json['features'][0])))
        conn.commit()

