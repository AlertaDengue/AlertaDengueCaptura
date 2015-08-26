import pandas as pd
import psycopg2
import geojson
import sys
import logging
from crawlclima.config.general import psql_host, psql_user

logger = logging.getLogger("crialoc")

try:
    conn = psycopg2.connect("dbname='dengue' user='{}' host='{}' password='alerta'".format(psql_user, psql_host))
    cur = conn.cursor()
except Exception as e:
    logger.error("Unable to connect to Postgresql: {}".format(e))
    sys.exit()




if __name__=="__main__":
    populações = pd.read_csv('popAPRJ.csv', header=0)
    bairrosAP = pd.read_csv("bairro2AP.csv", header=0)
    APS = populações.APS
    loc_id = dict([(str(k),j) for j,k in APS.iteritems()])
    sql = 'insert into "Municipio"."Bairro" (id, nome, Localidade_id) values(%s,%s,%s);'
    for i, bairro in bairrosAP.iterrows():
        registro = (i, bairro.bairro, loc_id[str(bairro.APS)])
        cur.execute(sql, registro)
    conn.commit()
    cur.close