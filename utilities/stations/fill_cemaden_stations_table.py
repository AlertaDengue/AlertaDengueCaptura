u"""
Created on 29/09/16
by fccoelho
license: GPL V3 or Later
"""

from io import StringIO

import pandas as pd
import psycopg2
import requests
from decouple import config

db_config = {
    "database": config("POSTGRES_DATABASE"),
    "user": config("POSTGRES_USER"),
    "password": config("POSTGRES_PASSWORD"),
    "host": config("POSTGRES_HOST"),
    "port": config("POSTGRES_PORT"),
}

base_url = "http://150.163.255.246:18383/dados_pcd"
chave = "bc10602ea62759fab1578f8eb1ff6f7abbf8678d"


def get_connection():
    try:
        conn = psycopg2.connect(
            "dbname='{}' user='{}' host='{}' password='{}'".format(
                db_config["database"],
                db_config["user"],
                "localhost",
                db_config["password"],
            )
        )
    except Exception as e:
        print("Unable to connect to Postgresql: {}".format(e))
        raise e
    return conn


def load_station_metadata(station_ID):
    con = get_connection()
    cur = con.cursor()
    sql = 'insert INTO "Municipio"."Estacao_cemaden" (codestacao,nome,municipio,uf,latitude,longitude) values(%s, %s, %s, %s, %s, %s);'
    results = requests.get(
        base_url,
        params={
            "chave": chave,
            "inicio": 201610050000,
            "fim": 201610051000,
            "rede": 11,
            "codigo": station_ID,
        },
    )
    df = pd.read_csv(StringIO(results.text), skiprows=1, header=0, delimiter=";")
    if df.size == 0:
        print("Station {} returned no data".format(station_ID))
        return 1
    # print(results.url)
    print(df.iloc[0]["cod.estacao"])
    record = {
        "codestacao": str(station_ID),
        "nome": df.iloc[0]["nome"],
        "municipio": df.iloc[0]["municipio"],
        "uf": df.iloc[0]["uf"],
        "latitude": float(df.iloc[0]["latitude"]),
        "longitude": float(df.iloc[0]["longitude"]),
    }
    try:
        cur.execute(
            sql,
            (
                record["codestacao"],
                record["nome"],
                record["municipio"],
                record["uf"],
                record["latitude"],
                record["longitude"],
            ),
        )
    except Exception as e:
        print("Could not insert {}: {}".format(station_ID, e))
        # raise(e)
    con.commit()
    cur.close()


def get_station_codes():
    """
    Get all CEMADEN station codes from database
    :return: list of tuples (code, UF)
    """
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        'select distinct "Estacao_cemaden_codestacao" from "Municipio"."Clima_cemaden";'
    )
    codes = cur.fetchall()
    cur.close()
    return codes


if __name__ == "__main__":
    for code in get_station_codes():
        load_station_metadata(code[0])
        # break
