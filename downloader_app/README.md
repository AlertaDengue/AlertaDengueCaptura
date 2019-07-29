# AlertaDengueCaptura - Downloader App

As rotinas disponíveis neste pacote foram feitas para a captura e processo imagens de satélite, de uma maneira fácil e conveniente. Além disso, há rotinas para combinar dados raster com camadas shapefiles afim de se obter imagens mais informativas. Confira o notebook *examples.ipynb* para ver como tudo funciona. 

## Requisitos

Para usar todas as funcionalidades, você precisará dos seguintes módulos:

    numpy
    pandas
    geopandas
    glob
    rasterio
    rasterstats
    shapely
    xarray
    netCDF4
    cartopy
    geoviews (version 1.6.2 or higher)
    celery
    rabbitmq-server
    flower

Geoviews é opcional pois é responsável por apenas algumas funções de visualização. Se você quiser essas funcionalidades, então o cartopy deve ser instalado antes do geoviews.

## Iniciando a captura

Primeiramente, rode o worker task.py com o comando 

	celery -A tasks worker --loglevel=info 

no terminal. Este comando inicializa o Celery, que poderá fazer os downloads de forma distribuída. Às vezes a opção 'loglevel=info' pode não ter informação o suficiente, neste caso pode-se trocar 'info' por 'debug'. Também pode ocorrer o contrário, quando não se deseja output algum além do mínimo necessário, neste caso simplesmente omita a opção loglevel.

Em outra aba do terminal, execute o comando 

	flower 

Este programa é opcional, mas ele é bastante conveniente para monitorar os downloads. Mais informações sobre este programa podem ser obtidas [aqui](https://flower.readthedocs.io/en/latest/). Após executá-lo, ele irá indicar um link para abrir navegador (http://localhost:5555). 

Agora podemos executar o programa para o download das imagens. Um exemplo de como isto é feito é mostrado abaixo.

![alt text](https://github.com/felipebottega/AlertaDengueCaptura/blob/master/downloader_app/readme_files/pic1.png)

A função acima recebe os seguintes parâmetros:

	source, date1, date2, point1, point2, opt

*source* se refere ao satélite de onde estamos pegando as imagens. Para ver as possíveis fontes, use o comando *td.about('sources')*.  *date1* e *date2* são a data inicial e a data final em que estamos interessados. Se a fonte obtiver imagens em uma frequência de 8 dias, o programa baixará todas as imagens segundo essa frequência entre *date1* e *date2*. Agora vamos ver as coordenadas espaciais. *point1* é uma tupla (x, y) correspondente ao ponto superior esquerdo da imagem, enquanto *point2* corresponde ao ponto inferior direito. Finalmente, *opt* é um dicionário com todas as variáveis opcionais de interesse. Essas variáveis são as descritas com o comando *td.about('options')*. Para fazer o download das imagens em seu formato original, sem nenhuma opção, passe o parâmetro 'options' como False. Neste exemplo passamos a opção 'regrid' para obter um tamanho maior (10 vezes maior em cada dimensão), utilizando o método 'cubic' para a interpolação dos pixels. Optamos por baixar as imagens do LandDAAC-v5-day, de 2016-jul-01 a 2016-set-30. 

O programa funciona fazendo o download da imagem, faz o tratamento da imagem de acordo com as opções passadas, e pode ou não manter a imagem original. Por default as imagens originais são mantidas, mas a opção *keep_original* pode ser mudada para False, daí apenas as imagens tratadas são mantidas no computador. Como neste exemplo esta opção não foi alterada, ela ficou no seu default e portanto as imagens originais também foram salvas para o computador. Abaixo nós mostramos duas imagens relativas ao mesmo arquivo raster baixado, uma delas sendo a original e outra a tratada.

![alt text](https://github.com/felipebottega/AlertaDengueCaptura/blob/master/downloader_app/readme_files/pic2.png)

## Trabalhando com shapefiles

É possível combinar dados raster com camadas shapefiles para obter imagens mais informativas. O módulo *shapefile_module* é responsável por esta parte. Neste exemplo nós estaremos trabalhando com o arquivo *WMP-2019/WMP2019_ReleaseAreas.shp*, que pode se encontra neste repositório, para propósitos de teste. Primeiramente, abrimos este arquivo com geopandas e utilizamos algumas funções básicas para obter informações e visualização.

![alt text](https://github.com/felipebottega/AlertaDengueCaptura/blob/master/downloader_app/readme_files/pic3.png)

Podemos obter o bounding box deste shapefile com o comando *min_x, max_x, min_y, max_y = sm.extract_shp_boundingbox(shp_filename)*. Note que *point1 = (min_x, max_y)* e *point2 = (max_x, min_y)* são exatamente as coordenadas usadas anteriormente para fazer os downloads dos arquivos raster. Isso foi proposital, pois queríamos obter os pixels relativos a este shapefile. Lembre que a primeira imagem baixada foi relativa à data 2016-jul-01. O arquivo original neste caso é '2016-07-01.tiff' enquanto que o tratado é 'new_2016-07-01.tiff'. Abaixo nós mostramos como fica o shapefile junto da imagem tratada relativa a esta data.

![alt text](https://github.com/felipebottega/AlertaDengueCaptura/blob/master/downloader_app/readme_files/pic4.png)

Uma das rotinas do módulo *shapefile_module* é obter o píxel médio relativo a cada polígono (neste caso o píxel médio por polígono representa a temperatura média por bairro na data) do shapefile, e então plotar a imagem onde cada polígono é colorido apenas com a cor do pixel médio. 

![alt text](https://github.com/felipebottega/AlertaDengueCaptura/blob/master/downloader_app/readme_files/pic5.png)

Lembre que diversos arquivos raster foram baixados, numa sequência temporal. Apesar de ser interessante obter a visualização das temperaturas médias em uma única data, pode ser ainda mais interessante obter a série temporal das temperaturas médias por bairro. Abaixo, mostramos como isso é possível para quatro bairros escolhidos. A quantidade de bairros na imagem é arbitrária, apenas se certifique de dar os nomes corretos (por default, os nomes são aqueles na segunda coluna do shapefile, neste caso, a coluna 'NOME_DO_BA').

![alt text](https://github.com/felipebottega/AlertaDengueCaptura/blob/master/downloader_app/readme_files/pic6.png) 










