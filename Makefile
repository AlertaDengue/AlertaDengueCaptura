# note: --env-file requires docker-compose>=1.25
#       ref: https://github.com/docker/compose/pull/6535

include $(ENVFILE)
export

compose_cmd = docker-compose -p alerta_out -f docker-compose.yml --env-file .env


build:
	$(compose_cmd) build

deploy: build
	$(compose_cmd) -d

stop:
	$(compose_cmd) stop