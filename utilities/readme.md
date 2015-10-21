#Carregamentos dos dados iniciais

os dados da tabela de municípios podem ser carregados, executando-se o script `cria_tabela_municipio.py`

A tabela de CID10 pode ser carregada com um simples `import` a partir do PGadmin3.

Para testar estes scripts de importação de dados, é preciso criar o banco localmente a partir do SQL em dbschema.



## Estações meteorológicas.
A tabela de estações meteorológicas (`utilities/stations/stations_seed.csv`) foi gerada a partir da [busca](http://bancodedados.cptec.inpe.br/tabelaestacoes/faces/consultapais.jsp) presente no site do [CPTEC/INPE](http://bancodedados.cptec.inpe.br/).

Apesar de termos a lista completa de estações do Brasil, só as estações de aeroportos (`utilities/stations/airport_stations_seed.csv`) possuem dados históricos no [WU](http://www.wunderground.com/), por isso, essas serão as carregadas para o Banco de Dados.

Para carregar os dados, basta executar:

```bash
$ python utilities/fill_stations.py
```
