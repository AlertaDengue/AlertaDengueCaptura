
#  AlertaDengueCaptura Utilities

### *Utilities contain some modules to update tables with initial data for use in the AlertaDengueCaptura.*

## Initial data loads

### Configure your virtual environment and install dependences using the environment.yml
Recommended to use conda , for quick installation:
https://docs.conda.io/en/latest/miniconda.html

*After installing the miniconda run:*

```bash
$ conda env create -f crawlclima/utilities/environment.yml

$ activate activate env-geos
```
### Install python packages
```
$ make install_crawlclima
```
### Create the database and schemas
```
$ make create_dbschemas
```
### Edit the .env file
Enter the path of the GeoJSONs in .env file and configure the variables for connection in the database.
```
$ vim crawlclima/crawlclima/.env
```
### Create directory utilities/geo_json/ | Convert and save geopandas to JSON
Before populating the data from municipalities, it is necessary to obtain the GeoJSONs from IBGE.
```
$ make get_geosbr
```

### Update geojson data
```
$ make run_fill_counties
```

### Update population
```
$ make update_mun_pop
```

### Weather stations

The meteorological stations table *"Municipio"."Estacao_wu"* was generated from the search present on the CPTEC/INPE website.
Although we have the complete list of stations in Brazil, only airport stations have historical data in the WU, so it was necessary to
filter those that had an [airport code](https://en.wikipedia.org/wiki/International_Civil_Aviation_Organization_airport_code) generating the **utilities/stations/airport_stations_seed.csv file.**

### Update airport codes in database
```
$ make update_fill_stations
```
---
## Scripts for data capture

*It should only be used for "manual" data capture, for automatic capture via CRON of the respective crawlclima package modules.*

### Capture data from tweets
This script captures a series of data from the dengue observatory server's tweets in various municipalities in a given period.
*Need create the log file*
```
$ sudo touch /var/log/crawlclima/capture-pegatweets.log
```
**Example**:
> $ python crawlclima/utilities/pega_tweets.py -i 2021-10-09 --fim 2021-10-17

### Weather data capture

This script captures a series of weather data from the stations in the Rede de Meteorologia do Comando da Aeronáutica in a given period.
*Need create the log file*
```
$ sudo touch /var/log/crawlclima/capture-pegatemperatura.log
```
**Example**:
> $ python crawlclima/utilities/pega_temperatura.py -c SBRJ -i 2021-09-28 -f 2021-10-01

</br>
---
