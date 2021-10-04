#!/usr/bin/env python

"""
Este script captura series de tweets do servidor do observatório da dengue em vários municipios.

Deve ser usado apenas para captura "manual" de tweets, para captura automática via CRON
use o modulo pegatweets do pacote crawlclima.

---
Example:
    // python crawlclima/utilities/pega_tweets.py -i 2021-10-09 --fim 2021-10-17 //
---

Copyright 2014 by Flávio Codeço Coelho
license: GPL v3
"""
import argparse
import datetime
from itertools import islice

from crawlclima.config.settings import local
from crawlclima.tasks import pega_tweets


def chunk(it, size):
    """
    divide a long list into sizeable chuncks
    :param it: iterable
    :param size: chunk size
    :return:
    """
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


with open(f'{local}/crawlclima/municipios') as f:
    municipios = f.read().split('\n')
    print(municipios)


date = lambda d: datetime.date.fromordinal(
    datetime.datetime.strptime(d, '%Y-%m-%d').toordinal()
)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    '--inicio', '-i', type=date, help='Data inicial de captura: yyyy-mm-dd'
)
parser.add_argument(
    '--fim', '-f', type=date, help='Data final de captura: yyyy-mm-dd'
)
args = parser.parse_args()

start, end = args.inicio, args.fim

for cidades in chunk(municipios, 50):
    print(
        'Fetching data start from {} to {} for {} '.format(
            start.isoformat(), end.isoformat(), cidades
        )
    )
    res = pega_tweets(
        inicio=start.isoformat(),
        fim=end.isoformat(),
        cidades=cidades,
        CID10='A90',
    )
    print('Successful! ', res)
