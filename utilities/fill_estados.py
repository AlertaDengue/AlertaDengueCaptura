#!/usr/bin/env python
import glob
import os

import geojson
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_config = {
    "database": os.getenv("PSQL_DB"),
    "user": os.getenv("PSQL_USER"),
    "password": os.getenv("PSQL_PASSWORD"),
    "host": os.getenv("PSQL_HOST"),
    "port": os.getenv("PSQL_PORT"),
}

path = os.getenv("GEOJSON_PATH")


def load_geojson(fname):
    with open(fname, "r") as f:
        return geojson.load(f)


if __name__ == "__main__":
    conn = psycopg2.connect(**db_config)
    with conn.cursor() as cur:
        for fname in glob.glob(os.path.join(path, "*-state.json")):
            print("Processing {}".format(fname))
            uf = os.path.split(fname)[1].split("-")[0]
            geo_json = load_geojson(fname)
            properties = geo_json["features"][0]["properties"]
            nome = properties["NM_ESTADO"]
            geocodigo = properties["CD_GEOCODU"]
            regiao = properties["NM_REGIAO"]
            cur.execute(
                'INSERT INTO "Dengue_global".estado (uf, nome, regiao, geocodigo, geojson) VALUES (%s,%s,%s,%s, %s)',
                (
                    uf,
                    nome,
                    regiao,
                    geocodigo,
                    geojson.dumps(geo_json["features"][0]),
                ),
            )
        conn.commit()
