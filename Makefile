# note: --env-file requires docker-compose>=1.25
#       ref: https://github.com/docker/compose/pull/6535

include $(ENVFILE)
export

.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

# Docker specific
ENV_FILE := crawlclima/.env
COMPOSE_FILE := crawlclima/docker/docker-compose.yml
DOCKER := PYTHON_VERSION=$(PYTHON_VERSION) docker-compose -p captura -f $(COMPOSE_FILE) --env-file $(ENV_FILE)
DOCKER_UP := $(DOCKER) up --remove-orphans -d --no-build
DOCKER_RUN := $(DOCKER) run --rm
DOCKER_BUILD := $(DOCKER) build
DOCKER_STOP := $(DOCKER) rm --force --stop
DOCKER_EXEC := $(DOCKER) exec
SERVICES := crawlclima

build_crawlclima:
	$(DOCKER_BUILD)

deploy_crawlclima:
	$(DOCKER_UP)

exec_crawlclima:
	$(DOCKER_EXEC) $(SERVICES) bash

stop_crawlclima:
	$(DOCKER_STOP)

restart_crawlclima: stop_crawlclima
	deploy_crawlclima

install_crawlclima: clean ## install the package to the active Python's site-packages

	cd crawlclima \
	&& envsubst < .env.tmpl > .env \
	&& python3 -m pip install -e .

develop_crawlclima: clean ## install the package in development mode
	cd crawlclima \
	&& python3 -m pip install -e '.[dev]' \
	&& pre-commit install


test_crawlclima:
	# Ignore tests in database, reason issue#56
	#--ignore=crawlclima/tests/test_tasks.py
	python -m pytest -vv crawlclima/ --ignore=crawlclima/tests/test_tasks.py


### UTILITIES
# Create database and import schemas
create_dbschemas: # create initials schemas and tables
	bash crawlclima/utilities/dbschema/create_db.sh

# Convert and save geopandas to JSON
get_geosbr:
	cd crawlclima \
	&& mkdir -p utilities/geo_json \
	&& python utilities/get_geosbr.py

# Update geojson data
run_fill_counties:
	cd crawlclima \
	&& python utilities/fill_counties.py

# Update population statistics
update_mun_pop:
	cd crawlclima \
	&& python utilities/update_mun_w_pop.py

# Update population statistics
update_fill_stations:
	cd crawlclima \
	&& python utilities/fill_stations.py

# Update population statistics
update_fill_states:
	cd crawlclima \
	&& python utilities/fill_estados.py

###
coverage: ## check code coverage quickly with the default Python
	coverage run --source crawlclima -m pytest -vv crawlclima --ignore=crawlclima/tests/test_tasks.py
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

### Clean ALL

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	rm -fr .idea/
	rm -fr */.eggs
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -fr {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	find . -name '*.ipynb_checkpoints' -exec rm -rf {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	find . -name '*.pytest_cache' -exec rm -rf {} +
