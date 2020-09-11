# note: --env-file requires docker-compose>=1.25
#       ref: https://github.com/docker/compose/pull/6535

include $(ENVFILE)
export

compose_cmd = docker-compose -f docker/crawlclima/docker-compose.yml --env-file .env


build_crawlclima:
	$(compose_cmd) build

deploy_crawlclima: build_crawlclima
	$(compose_cmd) up

stop_crawlclima:
	$(compose_cmd) stop

test_crawlclima:
	# Ignore tests in database, reason issue#56
	pytest -v crawlclima --ignore=crawlclima/tests/test_tasks.py


install_alertadenguecaptura:
	pip install -e .['develop']

clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
