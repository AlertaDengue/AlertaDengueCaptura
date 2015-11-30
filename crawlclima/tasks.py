from crawlclima.fetchapp import app
from celery.utils.log import get_task_logger
import requests
from crawlclima.config import cemaden
from io import StringIO
from datetime import datetime, timedelta
import time
from crawlclima.config.tweets import base_url, token, psql_db, psql_host, psql_user
import psycopg2
import csv

from crawlclima.wunderground.wu import capture_date_range
from utilities.models import save, find_all


logger = get_task_logger("Captura")

def get_connection():
    try:
        conn = psycopg2.connect("dbname='{}' user='{}' host='{}' password='aldengue'".format(psql_db, psql_user, psql_host))
    except Exception as e:
        logger.error("Unable to connect to Postgresql: {}".format(e))
        raise e
    return conn

@app.task
def mock(t):
    time.sleep(t)
    return "done"

@app.task(bind=True)
def pega_dados_cemaden(self, codigo, inicio, fim, by='uf'):
    """
    Esta tarefa captura dados climáticos de uma estação do CEMADEN, salvando os dados em um banco local.
    :param inicio: data-hora (UTC) de inicio da captura %Y%m%d%H%M
    :param fim: data-hora (UTC) de fim da captura %Y%m%d%H%M
    :param codigo: Código da estação de coleta do CEMADEN ou código de duas letras da uf: 'SP' ou 'RJ' ou...

    :param by: uf|estacao
    :return: Status code da tarefa
    """
    conn = get_connection()
    if isinstance(inicio, datetime):
        inicio = inicio.strftime("%Y%m%d%H%M")

    if isinstance(fim, datetime):
        fim = fim.strftime("%Y%m%d%H%M")

    try:
        assert (datetime.strptime(inicio, "%Y%m%d%H%M") < datetime.strptime(fim, "%Y%m%d%H%M"))
    except AssertionError:
        logger.error('data de início posterior à de fim.')
        raise AssertionError
    except ValueError as e:
        logger.error('Data mal formatada: {}'.format(e))
        raise ValueError

    # Check for latest records in the database
    cur = conn.cursor()
    cur.execute('select datahora from "Municipio"."Clima_cemaden" ORDER BY datahora DESC ')
    ultima_data = cur.fetchone()
    inicio = datetime.strptime(inicio, "%Y%m%d%H%M")
    fim = datetime.strptime(fim, "%Y%m%d%H%M")
    if ultima_data is not None:
        if ultima_data[0] > inicio:
            inicio = ultima_data[0]
        if inicio >= fim:
            return

    if by == 'uf':
        url = cemaden.url_rede
        pars = {'chave': cemaden.chave,
                'inicio': inicio.strftime("%Y%m%d%H%M"),
                'fim': fim.strftime("%Y%m%d%H%M"),
                'uf': codigo}
    elif by == 'estacao':
        url = cemaden.url_pcd
        pars = {'chave': cemaden.chave,
                'inicio': inicio.strftime("%Y%m%d%H%M"),
                'fim': fim.strftime("%Y%m%d%H%M"),
                'codigo': codigo}

    # puxa os dados do servidor do CEMADEN
    if fim-inicio > timedelta(hours=23, minutes=59):
        fim_t = inicio + timedelta(hours=23, minutes=59)
        data = []
        while fim_t < fim:
            pars['fim'] = fim_t.strftime("%Y%m%d%H%M")
            results = fetch_results(pars, url)
            try:
                vnames = results.text.splitlines()[1].strip().split(';')
            except IndexError as e:
                logger.warning("empty response from cemaden on {}-{}".format(inicio.strftime("%Y%m%d%H%M"), fim_t.strftime("%Y%m%d%H%M")))
            if not results.status_code == 200:
                continue # try again
            data += results.text.splitlines()[2:]
            fim_t += timedelta(hours=23, minutes=59)
            inicio += timedelta(hours=23, minutes=59)
            pars['inicio'] = inicio.strftime("%Y%m%d%H%M")
    else:
        results = fetch_results(pars, url)
        if isinstance(results, Exception):
            raise self.retry(exc=results, countdown=60)
        try:
            vnames = results.text.splitlines()[1].strip().split(';')
        except IndexError:
            logger.warning("empty response from cemaden on {}-{}".format(inicio.strftime("%Y%m%d%H%M"), fim.strftime("%Y%m%d%H%M")))
        if not results.status_code == 200:
            logger.error("Request to CEMADEN server failed with code: {}".format(results.status_code))
            raise self.retry(exc=requests.RequestException(), countdown=60)
        data = results.text.splitlines()[2:]

    save_to_cemaden_db(cur, data, vnames)

    conn.commit()
    cur.close()

    return results.status_code


def save_to_cemaden_db(cur, data, vnames):
    """
    Saves the rceived data to the "Clima_cemaden" table
    :param cur: db cursor
    :param data: data to be saved
    :param vnames: variable names in the server's response
    :return: None
    """
    vnames = [v.replace('.', '_') for v in vnames]
    sql = 'insert INTO "Municipio"."Clima_cemaden" (valor,sensor,datahora,"Estacao_cemaden_codestacao") values(%s, %s, %s, %s);'
    for linha in data:
        doc = dict(zip(vnames, linha.strip().split(';')))
        doc['latitude'] = float(doc['latitude'])
        doc['longitude'] = float(doc['longitude'])
        doc['valor'] = float(doc['valor'])
        doc['datahora'] = datetime.strptime(doc['datahora'], "%Y-%m-%d %H:%M:%S")
        cur.execute(sql, (doc['valor'], doc['sensor'], doc['datahora'], doc['cod_estacao']))



def fetch_results(pars, url):
    try:
        results = requests.get(url, params=pars)
    except requests.RequestException as e:
        logger.error("Request retornou um erro: {}".format(e))
        results = e
    except requests.ConnectionError as e:
        logger.error("Conexão falhou com erro {}".format(e))
        results = e
    return results


@app.task(bind=True)
def fetch_wunderground(self, station, date):
    try:
        logger.info("Fetching {}".format(station))
        data = capture_date_range(station, date)
        # data = [datum]
    except Exception as e:
        logger.error("Error fetching from {} at {}: {}".format(station, date, e))
    try:
        logger.info("Saving {}".format(station))
        if len(data) > 0:
            save(data, schema='Municipio', table='Clima_wu')
    except Exception as e:
        logger.error("Error saving to db with {} at {}: {}".format(station, date, e))



@app.task(bind=True)
def pega_tweets(self, inicio, fim, cidades=None, CID10="A90"):
    """
    Tarefa para capturar dados do Observatorio da dengue para uma ou mais cidades

    :param CID10: código CID10 para a doença. default: dengue clássico
    :param inicio: data de início da captura: yyyy-mm-dd
    :param fim: data do fim da captura: yyyy-mm-dd
    :param cidades: lista de cidades identificadas pelo geocódico(7 dig.) do IBGE - lista de strings.
    :return:
    """
    conn = get_connection()
    geocodigos = []
    for c in cidades:
        if len(str(c)) == 7:
            geocodigos.append((c, c[:-1]))
        else:
            geocodigos.append((c, c))
    cidades = [c[1] for c in geocodigos]
    params = "cidade=" + "&cidade=".join(cidades) + "&inicio="+str(inicio) + "&fim=" + str(fim) + "&token=" + token
    try:
        resp = requests.get('?'.join([base_url, params]))
        logger.info("URL ==> "+'?'.join([base_url, params]))
    except requests.RequestException as e:
        logger.error("Request retornou um erro: {}".format(e))
        raise self.retry(exc=e, countdown=60)
    except ConnectionError as e:
        logger.error("Conexão ao Observ. da Dengue falhou com erro {}".format(e))
        raise self.retry(exc=e, countdown=60)
    try:
        cur = conn.cursor()
    except NameError as e:
        logger.error("Not saving data because connection to database could not be established.")
        return e
    header = ["data"] + cidades
    fp = StringIO(resp.text)
    data = list(csv.DictReader(fp, fieldnames=header))
    #print(data)
    for i, c in enumerate(geocodigos):
        sql = """insert into "Municipio"."Tweet" ("Municipio_geocodigo", data_dia, numero, "CID10_codigo") values(%s, %s, %s, %s);""".format(c[0])
        for r in data[1:]:
            cur.execute('select * from "Municipio"."Tweet" where "Municipio_geocodigo"=%s and data_dia=%s;', (int(c[0]), datetime.strptime(r['data'], "%Y-%m-%d")))
            res = cur.fetchall()
            if res:
                continue
            cur.execute(sql, (c[0], datetime.strptime(r['data'], "%Y-%m-%d").date(), r[c[1]], CID10))
    conn.commit()
    cur.close()

    return resp.status_code

