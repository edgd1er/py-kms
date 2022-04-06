.PHONY: lint flake build help all

MAKEPATH := $(abspath $(lastword $(MAKEFILE_LIST)))
PWD := $(dir $(MAKEPATH))
CONTAINERS := $(shell docker ps -a -q -f "name=py-kms*")

#help:
#		@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# Fichiers/,/^# Base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## generate help list
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

all: hadolint lint flake build

actlint: ## use act to lint dockerfiles
		docker image pull ghcr.io/catthehacker/ubuntu:act-latest
		act -P ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-latest -rj lint

acttest: ## use act to test image: WIP
		docker image pull ghcr.io/catthehacker/ubuntu:full-latest
		act -P ubuntu-latest=ghcr.io/catthehacker/ubuntu:full-latest -rj test_build

actbuild: ## use act to build image
		docker image pull ghcr.io/catthehacker/ubuntu:full-latest
		docker image pull ghcr.io/catthehacker/ubuntu:act-latest

hadolint: ## lint dockerfiles
		@echo "lint dockerfile ..."
		docker image pull hadolint/hadolint
		docker run -i --rm hadolint/hadolint < docker/docker-py3-kms/Dockerfile
		docker run -i --rm hadolint/hadolint < docker/docker-py3-kms-minimal/Dockerfile

lint: ## lint python files
		pylint ./py-kms/

flake: ## lint python files
		flake8 ./py-kms/

build: ## build images
		@echo "Building image"
		@docker buildx build --progress auto --load -f docker/docker-py3-kms/Dockerfile -t edgd1er/py-kms .
		@echo "Building image minimal"
		@docker buildx build --progress auto --load -f docker/docker-py3-kms-minimal/Dockerfile -t py-kms-minimal .

down:
		docker compose -f docker-compose.yml -f docker/docker-py3-kms/Dockerfile down -v

up:
		docker compose -f docker-compose.yml up