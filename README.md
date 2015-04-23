# AlertaDengueCaptura
Rotinas para captura de dados

Este repo contem o código para as capturas automáticas de dados.

No diretório notebooks há alguns notebooks experimentais para testar os acessos e visualizar os dados.

Este repo contém uma framework para capturar dados de forma distribuída. Esta framework usa a bilbioteca Celery

##Requisitos

Para iniciar a captura é preciso ter installado o Rabbitmq-server e o Celery.

No Ubuntu:

```bash
$ sudo apt-get install rabbitmq-server

$ sudo pip3 install -U celery
```
## Iniciando a captura

para iniciar o rabbitmq:

```bash
$ sudo service rabbitmq-server start
```

Iniciando o Celery. dentro do diretório Crawlclima:

```bash
$ celery -A crawlclima.fetchapp worker --loglevel=info

```