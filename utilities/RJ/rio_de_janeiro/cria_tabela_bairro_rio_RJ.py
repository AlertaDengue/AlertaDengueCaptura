import logging
import sys

import pandas as pd
import psycopg2
from decouple import config

logger = logging.getLogger("criabairro")

try:
    conn = psycopg2.connect(
        "dbname='{}' user='{}' host='{}' password='{}'".format(
            config("POSTGRES_DATABASE").config("POSTGRES_USER"),
            config("POSTGRES_HOST"),
            config("POSTGRES_PASSWORD"),
        )
    )
    cur = conn.cursor()
except Exception as e:
    logger.error("Unable to connect to Postgresql: {}".format(e))
    sys.exit()


if __name__ == "__main__":
    populações = pd.read_csv("popAPRJ.csv", header=0)
    bairrosAP = pd.read_csv("bairro2AP.csv", header=0)
    APS = populações.APS
    loc_id = dict([(str(k), int(j)) for j, k in APS.iteritems()])
    sql = 'insert into "Municipio"."Bairro" (bairro_id, nome, "Localidade_id") values(%s,%s,%s);'
    for i, bairro in bairrosAP.iterrows():
        registro = (int(i), bairro.bairro, loc_id[str(bairro.APS)])
        cur.execute(sql, registro)
    conn.commit()
    cur.close
