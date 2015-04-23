from __future__ import absolute_import

from crawlclima.fetchapp import app
from celery.utils.log import get_task_logger
import requests
from crawlclima.config import cemaden
import pymongo
from io import StringIO
from datetime import datetime, timedelta

mongo = pymongo.MongoClient()

logger = get_task_logger(__name__)

@app.task
def pega_dados_cemaden(codigo, data, by='uf', recapture=False):
    """
    Esta tarefa captura dados climáticos de uma estação do CEMADEN, salvando os dados em um banco local.
    :param codigo: Código da estação de coleta do CEMADEN ou código de duas letras da uf: 'SP' ou 'RJ' ou...
    :param data: data-hora (UTC) de inicio da captura %Y%m%d%H%M
    :param by: uf|estacao
    :return: Status code da
    """
    if len(data) > 8:
        data = data[:8]
    data = datetime.strptime(str(data), "%Y%m%d")
    fim = data + timedelta(days=0, hours=23, minutes=59)
    if by == 'uf':
        url = cemaden.url_rede
        pars = {'chave': cemaden.chave,
                'inicio': data.strftime("%Y%m%d")+"0000",
                'fim': fim.strftime("%Y%m%d%H%M"),
                'uf': codigo}
    elif by == 'estacao':
        url = cemaden.url_pcd
        pars = {'chave': cemaden.chave,
                'inicio': data.strftime("%Y%m%d")+"0000",
                'fim': fim.strftime("%Y%m%d%H%M"),
                'codigo': codigo}
    col = mongo.clima.cemaden

    if not recapture:
        exists = col.find_one({"cod_estacao": codigo, "datahora": data})
        if exists is not None:
            logger.info("Registro já baixado. ignorando {}".format(data))
            return "Ignorando {}".format(data)
    try:
        results = requests.get(url, params=pars)
    except requests.RequestException as e:
        logger.error("Request retornou um erro: {}".format(e))
        return "falhou"
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

