# AlertaDengueCaptura
## Rotinas para captura de dados.

### Este repo contém uma framework para a captura automática de dados de forma distribuída  em dois diferentes aplicativos.  Esta framework usa a bilbioteca Celery.

<b> 1-Crawlclima<br></b>
<b> 2-Downloader App</b>

> *No diretório notebooks há alguns notebooks experimentais para testar os acessos e visualizar os dados.*
---
## Crawlclima

Captura de series tweets no servidor do observatório da dengue/UFMG.

### Requisitos (Ubuntu)

Para fazer o restore da base de dados baixe o projeto Data para executar os aplicativos com os dados do banco de dados de demonstração.  
Veja: https://github.com/AlertaDengue/Data

#### Clonar o repositório AlertaDengueCaptura
```bash
git clone https://github.com/AlertaDengue/AlertaDengueCaptura.git
```

#### Mover e renomear o arquivo env_sample  para o diretório AlertaDengueCaptura/crawlclima/
Modificar as variáveis de ambiente para a conexão com a base de dados demo no arquivo ".env".
```bash
$ mv  AlertaDengueCaptura/env_sample  AlertaDengueCaptura/crawlclima/.env
```
> *A partir de este passo todos os comandos devem ser executados no diretório do repo AlertaDengueCaptura$*

#### Install essentials and rabbitmq-server
```bash
$ sudo apt update -y \
&& sudo apt install build-essential libpq-dev \
&& git make wget vim \
&& rabbitmq-server
```
#### Criando e configurando o ambiente conda

Installing Miniconda
https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html

Após a instalação do miniconda execute:

```bash
$ conda create --name env_crawlclima pip

$ conda activate env_crawlclima

$ pip install -e .

```

### Iniciando o Celery

```bash
$ celery -A crawlclima.fetchapp worker --loglevel=info

```
### Iniciando a captura
> *Para executar as tarefas abra uma nova janela de terminal no diretório raiz do projeto AlertaDengueCaptura$:*

<i><i><b>Ativar o environment criado anteriormente</b></i></br>
``` $ conda activate env_crawlclima ```  
<i><i><b> Executar a tarefa Pegatweets </b></i></br>
``` $ python crawlclima/pegatweets.py ```  
<i><b> Executar a tarefa Pegatemperatura </b></i></br>
``` $ python crawlclima/pegatemperatura.py ```  
<i><b> Para captura automática via CRON use o arquivo crontab </b></i></br>
``` $ crontab -u $(whoami) crawlclima/crontab ```  
<i><b> Para editar o crontab </b></i></br>
``` $ crontab -e ```  
> Manual [crontab](https://man7.org/linux/man-pages/man5/crontab.5.html).

### Rodar o Crawlclima App em container(Docker)
Para build e deploy via docker consulte o [README](https://github.com/AlertaDengue/AlertaDengueCaptura/blob/master/docker/crawlclima/README.md) no diretório docker/crawlclima.


---
## Downloader App

As rotinas disponíveis neste pacote são projetadas para capturar e processar imagens de satélite de forma fácil e conveniente. Além disso, existem rotinas para combinar dados raster com camadas de shapefiles para imagens mais informativas [mais...](https://github.com/AlertaDengue/AlertaDengueCaptura/blob/master/downloader_app/README.md).

> Verifique o notebook [examples.ipynb](https://github.com/felipebottega/AlertaDengueCaptura/blob/master/downloader_app/examples.ipynb) para ver como funciona em detalhes.

### Requisitos

Para configurar o ambiente e instalar a app veja o [README](https://github.com/AlertaDengue/AlertaDengueCaptura/blob/master/downloader_app/README.md) no diretório downloader_app.

### Rodar o Downloader App em container(Docker)
Consulte o [README](https://github.com/AlertaDengue/AlertaDengueCaptura/blob/master/docker/satellite/README.md) no diretório docker/satellite.

> Esta app encontra-se em fase de desenvolvimento.
