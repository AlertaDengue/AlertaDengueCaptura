# note: --env-file requires docker-compose>=1.25
#       ref: https://github.com/docker/compose/pull/6535

include $(ENVFILE)
export


# docker specific
ENV_FILE := docker/crawlclima/.env
COMPOSE_FILE := docker/crawlclima/docker-compose.yml
DOCKER := PYTHON_VERSION=$(PYTHON_VERSION) docker-compose -f $(COMPOSE_FILE) --env-file $(ENV_FILE)
DOCKER_UP := $(DOCKER) up  --remove-orphans -d --no-build
DOCKER_RUN := $(DOCKER) run --rm
DOCKER_BUILD := $(DOCKER) build
DOCKER_STOP := $(DOCKER) rm --force --stop
DOCKER_EXEC := $(DOCKER) exec
SERVICES := capture_worker

MAKE = make -f docker/crawlclima/Makefile


build_crawlclima:
	$(DOCKER_BUILD)

deploy_crawlclima: build_crawlclima
	$(DOCKER_UP)

exec_crawlclima: #deploy_crawlclima
	$(DOCKER_EXEC) $(SERVICES) bash

stop_crawlclima:
	$(DOCKER_STOP)

restart_crawlclima: stop_crawlclima
	$(MAKE) deploy_crawlclima

install_alertadenguecaptura:
	pip install -e .['develop']


# TESTS
flake8_crawlclima:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

test_crawlclima:
	$(DOCKER_EXEC) -T $(SERVICES) pytest crawlclima/ -vv

clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '*.pyo' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
