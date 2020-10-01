# note: --env-file requires docker-compose>=1.25
#       ref: https://github.com/docker/compose/pull/6535

include $(ENVFILE)
export


# docker specific
ENV_FILE := downloader_app/.env
COMPOSE_FILE := docker/satellite/downloader-compose.yml
DOCKER := PYTHON_VERSION=$(PYTHON_VERSION) docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE)
DOCKER_UP := $(DOCKER) up  --remove-orphans -d --no-build
DOCKER_RUN := $(DOCKER) run --rm
DOCKER_BUILD := $(DOCKER) build
DOCKER_STOP := $(DOCKER) rm --force --stop
DOCKER_EXEC := $(DOCKER) exec
SERVICES := capture_worker

MAKE = make -f docker/satellite/Makefile


build_downloader_app:
	$(DOCKER_BUILD)

deploy_downloader_app: build_downloader_app
	$(DOCKER_UP)

exec_downloader_app: deploy_downloader_app
	$(DOCKER_EXEC) $(SERVICES) bash

stop_downloader_app:
	$(DOCKER_STOP) 

restart_downloader_app: stop_downloader_app
	$(MAKE) deploy_downloader_app

install_alertadenguecaptura:
	pip install -e .['develop']

configure_ci_downloader_app:
	bash .github/scripts/update_credentials_environ.sh
	python downloader_app/ci/create_credentials.py


# TESTS
flake8_downloader_app:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

test_downloader_app:
	$(DOCKER_EXEC) -T $(SERVICES) pytest downloader_app/ -vv

clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '*.pyo' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
