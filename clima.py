#!/usr/bin/env python
#coding:utf8
"""
Este script captura series de clima de estações do Rio de Janeiro
a partir do Weather underground

Copyright 2014 by Flávio Codeço Coelho
license: GPL v3
"""
import argparse
import datetime

from crawlclima.wunderground.wu import capture
from utilities.models import save, find_all


rows = find_all(schema='Municipio', table='Estacao_wu')
codes = [row['estacao_id'] for row in rows]


parser = argparse.ArgumentParser(description="Pega séries de Clima do servidor da Weather Underground em um período determinado")
parser.add_argument("--inicio", "-i", help="Data inicial de captura: yyyy-mm-dd")
parser.add_argument("--fim", "-f", help="Data final de captura: yyyy-mm-dd")
parser.add_argument("--codigo", "-c", choices=codes, help="Codigo da estação" )
args = parser.parse_args()
ini = datetime.datetime.strptime(args.inicio, "%Y-%m-%d")
fim = datetime.datetime.strptime(args.fim, "%Y-%m-%d")

data = capture(args.codigo, ini, fim)
save(data, schema='Municipio', table='Clima_wu')

