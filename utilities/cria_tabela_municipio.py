#-*- coding:utf-8 -*-
u"""
Created on 21/08/15
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'
import pandas as pd
import psycopg2
import geojson
from crawlclima.config.general import psql_host, psql_user
from multiprocessing.pool import Pool

try:
    conn = psycopg2.connect("dbname='dengue' user='{}' host='{}' password='aldengue'".format(psql_user, psql_host))
    cur = conn.cursor()
except Exception as e:
    logger.error("Unable to connect to Postgresql: {}".format(e))

siglas = {
    'Rondônia':'ro',
    'Pará': 'pa',
    'Amapá': 'ap',
    'Tocantins': 'to',
    'Maranhão': 'ma',
    'Piauí': 'pi',
    'Rio Grande do Norte': 'rn',
    'Paraíba': 'pb',
    'Alagoas': 'al',
    'Sergipe': 'se',
    'Bahia': 'ba',
    'Minas Gerais': 'mg',
    'São Paulo': 'sp',
    'Paraná': 'pr',
    'Santa Catarina': 'sc',
    'Rio Grande do Sul': 'rs',
    'Mato Grosso do Sul': 'ms',
    'Mato Grosso': 'mt',
    'Goiás': 'go',
    'Distrito Federal': 'df',
    'Acre': 'ac',
    'Amazonas': 'am',
    'Roraima': 'rr',
    'Ceará': 'ce',
    'Pernambuco': 'pe',
    'Espírito Santo': 'es',
    'Rio de Janeiro': 'rj'
}

#Carregando dados dos municipios
tabela_completa = pd.read_csv("DTB_2014_Municipio.csv")

def pega_poligono_municipio(uf, gc):
    """
    Carrega o geojson da UF e retorna o polígono correspondente ao município especificado pelo geocódigo.
    :param uf: Unidade da Federação
    :param gc: geocódigo do Município
    :return: Polígono do município (apenas a feature) como uma string.
    """
    gc = str(gc)
    sigla_uf = siglas[uf]
    UF_GeoJSON = geojson.load(open("/home/fccoelho/Copy/Projetos/Alerta_Dengue/mapas/br-atlas/geo/{}-counties.json".format(sigla_uf),"r"))
    try:
        pol = ""
        for p in UF_GeoJSON["features"]:
            if p["properties"]["CD_GEOCODM"] == gc:
                pol = p
                break
    except IndexError:
        print("Geocodigo possivelmente faltando na coleção de GeoJSONs: {}".format(gc))
        return ""
    return geojson.dumps(pol)

registros = []

def faz_tupla(mun):
    print(mun[0], mun[1]['Nome_Município'])
    return (mun[1]['Cod Municipio Completo'],
                       mun[1]['Nome_Município'],
                       pega_poligono_municipio(mun[1]['Nome_UF'], int(str(mun[1]['Cod Municipio Completo'])[:-1])),
                       0,
                       mun[1]['Nome_UF']
                       )

# Constroi os registros em paralelo
P = Pool()
registros = P.map(faz_tupla, tabela_completa.iterrows())

P.close()
P.join()
# for mun in tabela_completa.iterrows():
#     print(mun[0], mun[1]['Nome_Município'])
#     registros.append((mun[1]['Cod Municipio Completo'],
#                        mun[1]['Nome_Município'],
#                        pega_poligono_municipio(mun[1]['Nome_UF'], mun[1]['Cod Municipio Completo']),
#                        0,
#                        mun[1]['Nome_UF']
#                        ))
sql = '''insert into "Dengue_global"."Municipio" (geocodigo, nome, geojson, populacao, uf) values(%s, %s, %s, %s, %s);'''
cur.executemany(sql, list(registros))
conn.commit()
cur.close()
conn.close()


