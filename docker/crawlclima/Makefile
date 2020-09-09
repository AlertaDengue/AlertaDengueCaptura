# note: --env-file requires docker-compose>=1.25
#       ref: https://github.com/docker/compose/pull/6535

include $(ENVFILE)
export

compose_cmd = docker-compose -f docker-compose.yml --env-file .env


build:
	$(compose_cmd) build

deploy: build
	$(compose_cmd) up

stop:
	$(compose_cmd) stop

install:
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
