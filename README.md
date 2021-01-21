# AlertaDengueCaptura
Rotinas para captura de dados

Este repo contém o código para a capturas automáticas de dados em dois diferentes aplicativos;<br>
1-Crawlclima  
2-Downloader App

> No diretório notebooks há alguns notebooks experimentais para testar os acessos e visualizar os dados.
> Este repo contém uma framework para capturar dados de forma distribuída. Esta framework usa a bilbioteca Celery.

---
## Crawlclima

Captura de series tweets no servidor do observatório da dengue/UFMG.

### Requisitos

Para iniciar a captura é preciso ter instalado o Rabbitmq-server e o Celery.

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
### Executar a Crawlclima App em container(Docker)
Para build e deploy via docker consulte o [README](https://github.com/AlertaDengue/AlertaDengueCaptura/blob/master/docker/crawlclima/README.md) no diretório docker/crawlclima.

---
## Downloader App

As rotinas disponíveis neste pacote são projetadas para capturar e processar imagens de satélite de forma fácil e conveniente. Além disso, existem rotinas para combinar dados raster com camadas de shapefiles para imagens mais informativas... [mais detalhes](https://github.com/AlertaDengue/AlertaDengueCaptura/blob/master/docker/satellite/README.md)

### Requisitos

Para configurar o ambiente e instalar a app veja o [README](https://github.com/AlertaDengue/AlertaDengueCaptura/blob/master/downloader_app/README.md) no diretório downloader_app.

### Executar o Downloader App em container(Docker)
Consulte o [README](https://github.com/AlertaDengue/AlertaDengueCaptura/blob/master/docker/satellite/README.md) no diretório docker/satellite.

> Esta app encontra-se em fase de desenvolvimento.
