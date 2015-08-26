import pandas as pd
import psycopg2
import geojson
import sys
import logging

psql_user = "fill in"
psql_host = "127.0.0.1"

logger = logging.getLogger("crialoc")

try:
    conn = psycopg2.connect("dbname='dengue' user='{}' host='{}' password='alerta'".format(psql_user, psql_host))
    cur = conn.cursor()
except Exception as e:
    logger.error("Unable to connect to Postgresql: {}".format(e))
    sys.exit()

def pega_poligono_AP(ap, mapa):
    """
    A partir do mapa em formato geoJSON, extrai o polígono da AP
    :param ap: AP a extrair
    :param mapa: nome do arquivo
    :return: polígono
    """
    mun_GeoJSON = geojson.load(open(mapa, "r"))
    try:
        pol = ""
        for p in mun_GeoJSON["features"]:
            if p["properties"]["COD_AP_SMS"] == ap:
                pol = p
                break
    except IndexError:
        print("AP inexistente: {}".format(ap))
        return ""
    return pol



if __name__=="__main__":
    populações = pd.read_csv('popAPRJ.csv', header=0)
    APS = populações.APS
    sql = 'insert into "Municipio"."Localidade" (id,nome,populacao,geojson,Municipio_geocodigo) values(%s,%s,%s,%s,%s);'
    for i, ap in populações.iterrows():
        pol = pega_poligono_AP(str(ap.APS), "cap_sms.geojson")
        registro = (int(i), pol['properties']['NOME'], float(ap.Pop2010), geojson.dumps(pol), 3304557)
        cur.execute(sql, registro)
    conn.commit()
    cur.close