# note: --env-file requires docker-compose>=1.25
#       ref: https://github.com/docker/compose/pull/6535

include $(ENVFILE)
export

compose_cmd = docker-compose -f crawlclima/docker-compose.yml --env-file crawlclima/.env


build_crawlclima:
	$(compose_cmd) build

deploy_crawlclima: build_crawlclima
	$(compose_cmd) up

stop_crawlclima:
	$(compose_cmd) stop

install_crawlclima:
	pip install -e .['develop']

test:
	pytest crawlclima/ -v

clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
