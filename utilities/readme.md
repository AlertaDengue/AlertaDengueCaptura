#Carregamentos dos dados iniciais

Antes de tudo, é necessário criar o banco e os schemas, o que pode ser feito através do comando:

```bash
$ psql < dbschema/dengue.sql
```

## CID-10

A tabela de CID10 pode ser carregada com um simples `import` a partir do PGadmin3.

## Municípios.

Antes de popular os dados de municípios, é necessário obter os GeoJSONs do IBGE. Para isso, é necessário usar o código disponível em carolinabigonha/br-atlas@9a3839c.

Depois disso, basta informar o caminho dos GeoJSONs no `settings.ini` e rodar o seguinte comando:

```bash
$ python utilities/fill_counties.py
```

## Estações meteorológicas.

A tabela de estações meteorológicas (`utilities/stations/stations_seed.csv`) foi gerada a partir da [busca](http://bancodedados.cptec.inpe.br/tabelaestacoes/faces/consultapais.jsp) presente no site do [CPTEC/INPE](http://bancodedados.cptec.inpe.br/).

Apesar de termos a lista completa de estações do Brasil, só as estações de aeroportos possuem dados históricos no [WU](http://www.wunderground.com/), por isso, houve a necessidade de filtrar as que possuíam [código de aeroporto](https://en.wikipedia.org/wiki/International_Civil_Aviation_Organization_airport_code) gerando o arquivo `utilities/stations/airport_stations_seed.csv`.

Para carregar esses dados para o banco, basta executar:

```bash
$ python utilities/fill_stations.py
```
