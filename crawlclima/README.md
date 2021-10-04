# Crawlclima

<p style="font-size:18px" >Este pacote contém os módulos <i><small>PEGATWEETS</i></small> e <i><small>PEGATEMPERATURA</i></small> para captura automática de tweets e dados climáticos.</p>

### Requisitos<small>(Debian)</small>

#### Instalar essentials, postgresql e rabbitmq-server
```bash
$ sudo apt-get -qq update --yes \
  && apt-get -qq install --yes --no-install-recommends \
  && build-essential ca-certificates libpq-dev locales \
  && rabbitmq-server postgres postgresql-client vim wget git make cron \
  && rm -rf /var/lib/apt/lists/*
```
#### Clonar o repositório AlertaDengueCaptura
```bash
$ git clone https://github.com/AlertaDengue/AlertaDengueCaptura.git
```

#### Criando e configurando o ambiente conda

*Installing Miniconda:*
https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html

*Após a instalação do miniconda execute:*

```bash
$ conda env create -f docker/crawlclima/environment.yml

$ conda activate captura-crawlclima
```

#### Instalar os pacotes do projeto e criar arquivo de ambiente .env
```bash
$ make install_crawlclima
```

#### Configurar o banco de dados demo

- *Para poder executar as tarefas de captura com os dados do banco de dados de demonstração baixe o repositório [AlertaDengue/Data](https://github.com/AlertaDengue/Data) . Ou use os [utilitários](https://github.com/AlertaDengueCaptura/AlertaDengueCaptura/blob/crawlclima-refactore/crawlclima/utilities/README.md) para criação do banco e os schemas iniciais.*
- *Modificar as variáveis de conexão com a base de dados de demonstração e as demais variáveis de ambiente no arquivo de ambiente; **AlertaDengueCaptura/crawlclima/.env** do projeto.*

### Iniciando o Celery e rabbbitmq

*Insira na variável de ambiente o endereço de conexão para:*
**CELERY_BROKER_URL='amqp://guest:guest@127.0.0.1:5672**

*Execute os seguintes comandos:*
```bash
$ rabbitmq-server start -detached

$ celery -A crawlclima.fetchapp worker --concurrency=8 -l INFO --logfile=logs/celery-tasks.log
```
*Para mais detalhes consulte a documentação:*
[RabbitMQ](https://www.rabbitmq.com/networking.html
)
[Celery](https://docs.celeryproject.org/en/stable/userguide/configuration.html)

### Iniciando a captura

*Em uma nova janela do console/shell execute as tarefas desde o diretório raiz do projeto:*</br>

<i><i><b>Ativar o ambiente conda criado anteriormente</b></i>
``` $ conda activate captura-crawlclima ```
<i><i><b> Executar a tarefa Pegatweets </b></i>
``` $ python crawlclima/crawlclima/pegatweets.py ```
<i><b> Executar a tarefa Pegatemperatura </b></i>
> Para poder acessar as informações disponibilizadas pela APIs, será necessário a [realização de um cadastro e obter uma chave](https://www.atd-1.com/cadastro-api/)

``` $ python crawlclima/crawlclima/pegatemperatura.py ```
<i><b> Para captura automática via CRON use o arquivo crontab </b></i>
``` $ crontab -u $(whoami) crawlclima/crawlclima/cron_tasks ```
<i><b> Para editar o crontab </b></i>
``` $ crontab -e ```
> Manual [crontab](https://man7.org/linux/man-pages/man5/crontab.5.html).

### Deploy crawlclima in container<small>(Docker)</small>
####  Get Docker
*https://docs.docker.com/engine/install/ubuntu/*
#### Install Docker Compose:
*https://docs.docker.com/compose/install/*

#### Build and run containers

> Use the make command within the root directory AlertDengueCapture/:<br>
```bash
$ make install_crawlclima
$ make build_crawlclima
$ make deploy_crawlclima
$ make stop_crawlclima
```
---
