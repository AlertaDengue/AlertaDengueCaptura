from __future__ import absolute_import

from crawlclima.celery import app
import requests
from crawlclima.config import cemaden
import pymongo
from io import StringIO
from datetime import datetime

mongo = pymongo.MongoClient()


@app.task
def pega_dados_por_estacao(codigo, inicio, fim, recapture=False):
    """
    Esta tarefa captura dados climáticos de uma estação do CEMADEN, salvando os dados em um banco local.
    :param codigo: Código da estação de coleta do CEMADEN
    :param inicio: data-hora (UTC) de inicio da captura %Y%m%d%H%M
    :param fim: data-hora (UTC) de fim da captura %Y%m%d%H%M
    :return: Status code da
    """
    col = mongo.clima.cemaden
    if not recapture:
        exists = col.find({"cod_estacao": codigo, "datahora": datetime.strptime(str(inicio), "%Y%m%d%H%M")}).count()
        if exists:
            return "skipping {}".format(inicio)
    #TODO: validar o código de estação
    results = requests.get(cemaden.url_pcd, params={'chave': cemaden.chave,
                                        'inicio': inicio,
                                        'fim': fim,
                                        'codigo': codigo})
    fp = StringIO(results.text)
    fp.readline()  # Remove o comentário
    vnames = fp.readline().strip().split(';')
    vnames = [v.replace('.', '_') for v in vnames]
    for linha in fp:
        doc = dict(zip(vnames, linha.strip().split(';')))
        col.insert(doc)

    return results.status_code


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)