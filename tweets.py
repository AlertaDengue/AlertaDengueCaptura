#!/usr/bin/env python3

"""
Este script captura series de tweets do servidor do observatório da dengue em vários municipios.

Deve ser usado apenas para captura "manual" de tweets, para captura automática via CRON use o script pegatweets do pacote
crawlclima.


Copyright 2014 by Flávio Codeço Coelho
license: GPL v3
"""
import argparse
import datetime

from crawlclima.tasks import pega_tweets

with open("municipios") as f:
    municipios = f.read().split("\n")


date = lambda d: datetime.date.fromordinal(
    datetime.datetime.strptime(d, "%Y-%m-%d").toordinal()
)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--inicio", "-i", type=date, help="Data inicial de captura: yyyy-mm-dd"
)
parser.add_argument("--fim", "-f", type=date, help="Data final de captura: yyyy-mm-dd")
args = parser.parse_args()

start, end = args.inicio, args.fim

pega_tweets(start.isoformat(), fim=end.isoformat(), cidades=municipios, CID10="A90")
