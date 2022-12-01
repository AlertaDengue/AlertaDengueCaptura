# AlertaDengueCaptura
[![codecov](https://codecov.io/gh/AlertaDengue/AlertaDengueCaptura/branch/master/graph/badge.svg?token=MF2CCDUX6A)](https://codecov.io/gh/AlertaDengue/AlertaDengueCaptura)![flujo de trabajo de ejemplo](https://github.com/AlertaDengue/AlertaDengueCaptura/actions/workflows/main.yaml/badge.svg)[![Build Status](https://img.shields.io/appveyor/ci/thiagoloureiro/netcore-jwt-integrator-extension/master.svg)](https://ci.appveyor.com/project/thiagoloureiro/netcore-jwt-integrator-extension)

## Rotinas para captura de dados.

### Este repositório contém uma framework para a captura automática de dados de forma distribuída  em dois diferentes aplicativos:

### Crawlclima

- Captura de séries tweets no servidor do [observatório da dengue/UFMG](https://observatorio.inweb.org.br/).
- Captura os dados das estações meteorológicos [REDEMET](https://www.redemet.aer.mil.br/) dos aeroportos.

#### Requisitos<small>(Debian)</small>

Para configurar o ambiente e instalar a app veja o [README](https://github.com/AlertaDengue/AlertaDengueCaptura/tree/main/crawlclima/README.md) no diretório crawclima.
> *[Utilities](https://github.com/AlertaDengue/AlertaDengueCaptura/blob/main/utilities/README.md) contain some tools and modules to update tables with initial data for use in the AlertaDengueCaptura.*
---
### Downloader
- As rotinas disponíveis neste pacote são projetadas para capturar e processar imagens de satélite de forma fácil e conveniente. Além disso, existem rotinas para combinar dados raster com camadas de shapefiles para imagens mais informativas [mais...](https://github.com/AlertaDengue/AlertaDengueCaptura/blob/master/downloader_app/README.md).
- Verifique o notebook [examples.ipynb](https://github.com/felipebottega/AlertaDengueCaptura/blob/master/downloader_app/examples.ipynb) para ver como funciona em detalhes.

#### Requisitos<small>(Debian)</small>

Para configurar o ambiente e instalar a app veja o [README](https://github.com/AlertaDengue/AlertaDengueCaptura/blob/master/downloader_app/README.md) no diretório downloader_app.


> *No diretório notebooks há mais [notebooks](https://github.com/AlertaDengue/AlertaDengueCaptura/tree/main/notebooks) experimentais para testar os acessos e visualizar os dados.*
#### Rodar o Downloader App em container<small>(Docker)</small>

Consulte o [README](https://github.com/AlertaDengue/AlertaDengueCaptura/blob/master/docker/satellite/README.md) no diretório docker/satellite.

> Esta app encontra-se em fase de desenvolvimento, [contribua](https://github.com/AlertaDengue/AlertaDengueCaptura/tree/main/downloader_app)...
---

### To update the CrawlClima submodule within the AlertaDengueCaptura repository:
```
$ cd CrawlClima/
$ git submodule update
$ git checkout --recurse-submodules main
$ git pull --recurse-submodules
```
and then, update from the main repo AlertaDengueCaptura:
```
$ cd ..
$ git status
On branch refactor-structure
Your branch is up to date with 'origin/refactore-structure'.

Changes not staged for commit:
   (use "git add <file>..." to update what will be committed)
   (use "git restore <file>..." to discard changes in working directory)
         modified: CrawlClima (new commits)
$ git add -u
$ git status
$ git commit -m "Update CrawlClima submodule"
$ git push
```
