from __future__ import absolute_import

from crawlclima.celery import app
import requests
from crawlclima import config
import pymongo


mongo = pymongo.MongoClient()


@app.task
def pega_dados_por_estacao(codigo, inicio, fim):
    """
    Esta tarefa captura dados climáticos de uma estação do CEMADEN, salvando os dados em um banco local.
    :param codigo: Código da estação de coleta do CEMADEN
    :param inicio: data-hora (UTC) de inicio da captura %Y%m%d%H%M
    :param fim: data-hora (UTC) de fim da captura %Y%m%d%H%M
    :return: Status code da
    """
    #TODO: validar o código de estação
    results = requests.get(config.cemaden.url_pcd, params={'chave': config.cemaden.chave,
                                        'inicio': inicio,
                                        'fim': fim,
                                        'codigo': codigo})
    return results.status_code


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)