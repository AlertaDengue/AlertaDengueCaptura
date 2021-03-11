# Install packages and utilities

include .env


# Install python packages
install_alertadenguecaptura:
	pip install -e .

# Create directory utilities/geo_json/
# Convert and save geopandas to JSON 
 get_geosbr:
	mkdir -p utilities/geo_json
	python utilities/get_geosbr.py

# Update geojson data
run_fill_counties:
	python utilities/fill_counties.py

# Update population statistics
update_mun_pop:
	python utilities/update_mun_w_pop.py
