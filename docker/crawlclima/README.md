# AlertaDengueCaptura
Routines for data capture.<br>
This repo contains the code for automatic capture of climatic data by the Crawlclima app schedule by crontab.

## Deploying Crawlclima with Docker

#### Requirements

Download the Data project to run the apps as the data from the demo databes.<br>
See: https://github.com/AlertaDengue/Data

#### Configure environment
Copy the env_sample file by renaming it to .env into the docker/crawlclima directory:
```bash
cp /docker/crawclima/env_sample /docker/crawclima/.env
```
Modify the variables of file system and database connection according to needs.

#### Update and install essentials
```bash
$ sudo apt update -y \
&& sudo apt install build-essential libpq-dev \
&& git make wget vim
```
####  Get Docker
*https://docs.docker.com/engine/install/ubuntu/*
#### Install Docker Compose: 
*https://docs.docker.com/compose/install/*

#### Build and run containers
> Use the make command within the root directory AlertDengueCapture/:<br>
```bash
$ make -f docker/crawlclima/Makefile install_alertadenguecaptura
$ make -f docker/crawlclima/Makefile build_crawlclima
$ make -f docker/crawlclima/Makefile deploy_crawlclima
```
> The crontab schedule can be edited manually in the file:<br>
```bash
$ vim docker/crawlclima/cron_tasks
```
> After modifying the crontab you will need to do a new build and deploy. <br>
> It is also possible to modify it using the "crontab -e" page inside the Crawlclima app container.<br>

### Others Make commands

<i><i><b> build services to images docker </b></i></br>
``` $ make -f docker/crawlclima/Makefile build_crawlclima ```</br>
<i><b> Run containers and start services </b></i></br>
``` $ make -f docker/crawlclima/Makefile deploy_crawlclima ```</br>
<i><b> Entry into container for crawlclima </b></i></br>
``` $ make -f docker/crawlclima/Makefile exec_crawlclima ```</br>
<i><b>  Stop an remove containers </b></i></br>
``` $ make -f docker/crawlclima/Makefile stop_crawlclima ```</br>
<i><b> Restart containers </b></i></br>
``` $ make -f docker/crawlclima/Makefile restart_crawlclima ```</br>
<i><b> Configure project and install requirements dev </b></i></br>
``` $ make -f docker/crawlclima/Makefileinstall_alertadenguecaptura ```</br>
<i><b> Clean containers </b></i></br>
``` $ make -f docker/crawlclima/Makefile clean ```</br>
<i><b> Run tests into container </b></i></br>
``` $ make -f docker/crawlclima/Makefile flake8_crawlclima ```</br>
``` $ make -f docker/crawlclima/Makefile test_crawlclima ```</br>
