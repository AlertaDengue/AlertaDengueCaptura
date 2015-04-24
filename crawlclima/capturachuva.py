#!/usr/bin/env python3

from datetime import datetime, timedelta
from crawlclima.tasks import pega_dados_cemaden, mock

# Data inicial da captura

inicio = datetime(2014, 7, 1)

hoje = datetime.today()

data = inicio
while data <= hoje:
    pega_dados_cemaden.delay('RJ', data.strftime("%Y%m%d%H%M"))
    #mock.delay(5)
    data += timedelta(1)