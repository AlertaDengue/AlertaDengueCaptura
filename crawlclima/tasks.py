from __future__ import absolute_import

from crawlclima.fetchapp import app
from celery.utils.log import get_task_logger
import requests
from crawlclima.config import cemaden
import pymongo
from io import StringIO
from datetime import datetime, timedelta
import time
from crawlclima.config.tweets import base_url, token, psql_db, psql_host, psql_user
import psycopg2
import csv



mongo = pymongo.MongoClient()

logger = get_task_logger("Captura")

try:
    conn = psycopg2.connect("dbname='{}' user='{}' host='{}' password='alerta'".format(psql_db, psql_user, psql_host))
except Exception as e:
    logger.error("Unable to connect to Postgresql: {}".format(e))

@app.task
def mock(t):
    time.sleep(t)
    return "done"

@app.task
def pega_dados_cemaden(codigo, inicio, fim, by='uf'):
    """
    Esta tarefa captura dados climáticos de uma estação do CEMADEN, salvando os dados em um banco local.
    :param inicio: data-hora (UTC) de inicio da captura %Y%m%d%H%M
    :param fim: data-hora (UTC) de fim da captura %Y%m%d%H%M
    :param codigo: Código da estação de coleta do CEMADEN ou código de duas letras da uf: 'SP' ou 'RJ' ou...

    :param by: uf|estacao
    :return: Status code da tarefa
    """
    try:
        assert (datetime.strptime(inicio, "%Y%m%d%H%M") < datetime.strptime(fim, "%Y%m%d%H%M"))
    except AssertionError:
        logger.error('data de início posterior à de fim.')
        raise AssertionError
    except ValueError as e:
        logger.error('Data mal formatada: {}'.format(e))
        raise ValueError

    if by == 'uf':
        url = cemaden.url_rede
        pars = {'chave': cemaden.chave,
                'inicio': inicio,
                'fim': fim,
                'uf': codigo}
    elif by == 'estacao':
        url = cemaden.url_pcd
        pars = {'chave': cemaden.chave,
                'inicio': inicio,
                'fim': fim,
                'codigo': codigo}
    col = mongo.clima.cemaden
    col.create_index([("nome", pymongo.ASCENDING),
                    ("cod_estacao", pymongo.ASCENDING),
                    ("datahora", pymongo.DESCENDING)],
                     background=True
                      )
    try:
        results = requests.get(url, params=pars)
    except requests.RequestException as e:
        logger.error("Request retornou um erro: {}".format(e))
        raise self.retry(exc=e, countdown=60)
    except requests.ConnectionError as e:
        logger.error("Conexão falhou com erro {}".format(e))
        raise self.retry(exc=e, countdown=60)


    fp = StringIO(results.text)
    fp.readline()  # Remove o comentário
    vnames = fp.readline().strip().split(';')
    vnames = [v.replace('.', '_') for v in vnames]
    subs = 0
    for linha in fp:
        doc = dict(zip(vnames, linha.strip().split(';')))
        doc['latitude'] = float(doc['latitude'])
        doc['longitude'] = float(doc['longitude'])
        doc['valor'] = float(doc['valor'])
        doc['datahora'] = datetime.strptime(doc['datahora'], "%Y-%m-%d %H:%M:%S")
        mongo_result = col.replace_one({"cod_estacao": doc['cod_estacao'], "datahora": doc['datahora'], "nome": doc['nome']}, doc, upsert=True)
        subs += mongo_result.modified_count
    logger.info("Registros Substituídos: {}".format(subs))
    return results.status_code


@app.task
def pega_dados_wunderground(uf, inicio, fim, recapture=False):

    return

@app.task
def pega_tweets(inicio, fim, cidades=None, CID10="A90"):
    """
    Tarefa para capturar dados do Observatorio da dengue para uma ou mais cidades

    :param CID10: código CID10 para a doença. default: dengue clássico
    :param inicio: data de início da captura: yyyy-mm-dd
    :param fim: data do fim da captura: yyyy-mm-dd
    :param cidades: lista de cidades identificadas pelo geocódico do IBGE.
    :return:
    """

    cidades = [int(c) for c in cidades]
    params = "cidade=" + "&cidade=".join(cidades) + "&inicio="+str(inicio) + "&fim=" + str(fim) + "&token=" + token
    try:
        resp = requests.get('?'.join([base_url, params]))
    except requests.RequestException as e:
        logger.error("Request retornou um erro: {}".format(e))
        raise self.retry(exc=e, countdown=60)
    except ConnectionError as e:
        logger.error("Conexão ao Obs. da Dengue falhou com erro {}".format(e))
        raise self.retry(exc=e, countdown=60)
    try:
        cur = conn.cursor()
    except NameError as e:
        logger.error("Not saving data because connection to database has not been established.")
        return e
    header = ["data"] + cidades
    fp = StringIO(resp.text)
    data = list(csv.DictReader(fp, fieldnames=header))
    #print(data)
    for i, c in enumerate(cidades):
        sql = """insert into "Municipio"."Tweet" ("Municipio_geocodigo", data_dia, numero, "CID10_codigo") values(%s, %s, %s, %s);""".format(c)
        for r in data[1:]:
            cur.execute('select * from "Municipio"."Tweet" where "Municipio_geocodigo"=%s and data_dia=%s;')
            res = cur.fetchall()
            if not res:
                continue
            cur.execute(sql, (c, datetime.strptime(r['data'], "%Y-%m-%d").date(), r[c], CID10))
    conn.commit()
    cur.close()

    return resp.status_code

