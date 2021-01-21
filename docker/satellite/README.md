# AlertaDengueCaptura
Routines for data capture.  
The routines available in this package are designed to capture and process satellite images by scheduling the Downloader App with the crontab.

## Deploying Downloader App with Docker

#### Requirements

Download the Data project to run the apps as the data from the demo databes.<br>
See: https://github.com/AlertaDengue/Data

#### Configure environment
Copy the example_env file by renaming it to .env into the docker/satellite directory:
```bash
cp example_env_file /docker/satellite/.env
```
Modify the variables of file system and database connection according to needs.

#### Update and install essentials
```bash
$ sudo apt update && sudo apt -y upgrade \
  build-essential git make wget vim
```
####  Get Docker
*https://docs.docker.com/engine/install/ubuntu/*
#### Install Docker Compose: 
*https://docs.docker.com/compose/install/*

#### Build and run containers
> Use the make command within the root directory AlertDengueCapture/:  
```bash
$ make -f docker/satellite/Makefile install_alertadenguecaptura
$ make -f docker/satellite/Makefile configure_ci_downloader_app
$ make -f docker/satellite/Makefile build_downloader_app
$ make -f docker/satellite/Makefile deploy_downloader_app
```
> The crontab schedule can be edited manually in the file:  
```bash
$ vim docker/satellite/cron_tasks
```
> After modifying the crontab you will need to do a new build and deploy.  
> It is also possible to modify it using the "crontab -e" page inside the Downloader app container.  

### Others Make commands

<i><i><b> build services to images docker </b></i></br>
``` $ make -f docker/satellite/Makefile build_downloader_app ```  
<i><b> Run containers and start services </b></i></br>
``` $ make -f docker/satellite/Makefile deploy_downloader_app ```  
<i><b> Entry into container for crawlclima </b></i></br>
``` $ make -f docker/satellite/Makefile exec_downloader_app ```  
<i><b>  Stop and remove containers </b></i></br>
``` $ make -f docker/satellite/Makefile stop_downloader_app ```  
<i><b> Restart containers </b></i>  
``` $ make -f docker/satellite/Makefile restart_downloader_app ```  
<i><b> Configure project and install requirements dev </b></i>  
``` $ make -f docker/satellite/Makefile install_alertadenguecaptura ```  
<i><b> Configure credentials for earth-engine </b></i></br>
``` $ make -f docker/satellite/Makefile configure_ci_downloader_app ```  
<i><b> Clean containers </b></i></br>
``` $ make -f docker/satellite/Makefile clean ```  
<i><b> Run tests into container </b></i>  
``` $ make -f docker/satellite/Makefile flake8_downloader_app ```  
``` $ make -f docker/satellite/Makefile test_downloader_app ```  
