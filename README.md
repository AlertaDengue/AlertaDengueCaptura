# AlertaDengueCaptura
Rotinas para captura de dados

Este repo contém o código para a capturas automáticas de dados em dois diferentes aplicativos;<br>
1-Crawlclima<br>
2-Downloader_app

> No diretório notebooks há alguns notebooks experimentais para testar os acessos e visualizar os dados.
> Este repo contém uma framework para capturar dados de forma distribuída. Esta framework usa a bilbioteca Celery.

## Crawlclima

Captura de series tweets no servidor do observatório da dengue/UFMG.

### Requisitos

Para iniciar a captura é preciso ter installado o Rabbitmq-server e o Celery.

No Ubuntu:

```bash
$ sudo apt-get install rabbitmq-server

$ sudo pip3 install -U celery
```
### Iniciando a captura

para iniciar o rabbitmq:

```bash
$ sudo service rabbitmq-server start
```

Iniciando o Celery. dentro do diretório Crawlclima:

```bash
$ celery -A crawlclima.fetchapp worker --loglevel=info

```
### Executar a app Crawlclima em container(Docker)
Para build e deploy via docker consulte o [README](https://github.com/AlertaDengue/AlertaDengueCaptura/docker/crawlclima/README.md) dentro do diretório docker/crawlclima.

## Downloader_app

Captura e tratamento de imagens de satélite de Google Earth.

### Requisitos
O Downloader_app é executado apenas em container(docker) consulte o [README](https://github.com/AlertaDengue/AlertaDengueCaptura/docker/satellite/README.md) dentro do diretório docker/satellite.
> Esta app encontra-se em fase de desenvolvimento.
