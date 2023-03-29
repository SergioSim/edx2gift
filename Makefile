# -- General
SHELL := /bin/bash

# -- Docker
# Get the current user ID to use for docker run and docker exec commands
DOCKER_UID           = $(shell id -u)
DOCKER_GID           = $(shell id -g)
DOCKER_USER          = $(DOCKER_UID):$(DOCKER_GID)
COMPOSE              = DOCKER_USER=$(DOCKER_USER) docker compose
COMPOSE_RUN          = $(COMPOSE) run --rm --no-deps
COMPOSE_RUN_APP      = $(COMPOSE_RUN) app

# -- Edx2gift
EDX2GIFT_IMAGE_BUILD_TARGET ?= development
EDX2GIFT_IMAGE_NAME         ?= edx2gift
EDX2GIFT_IMAGE_TAG          ?= development
EDX2GIFT_SERVER_PORT        ?= 8100


# ======================================================================================
# RULES
# ======================================================================================

default: help

.env:
	cp .env.dist .env

# -- Docker/compose
bootstrap: ## bootstrap the project for development
bootstrap: \
  .env \
  build
.PHONY: bootstrap

build: ## build the app container
	EDX2GIFT_IMAGE_BUILD_TARGET=$(EDX2GIFT_IMAGE_BUILD_TARGET) \
	EDX2GIFT_IMAGE_NAME=$(EDX2GIFT_IMAGE_NAME) \
	EDX2GIFT_IMAGE_TAG=$(EDX2GIFT_IMAGE_TAG) \
	  $(COMPOSE) build app
.PHONY: build

down: ## stop and remove app containers
	@$(COMPOSE) down
.PHONY: down

logs: ## display app logs (follow mode)
	@$(COMPOSE) logs -f
.PHONY: logs

run: ## run the edx2gift server
	@$(COMPOSE) up -d app
.PHONY: run

status: ## an alias for "docker compose ps"
	@$(COMPOSE) ps
.PHONY: status

stop: ## stop app server
	@$(COMPOSE) stop
.PHONY: stop

# -- Linters
#
# Nota bene: Black should come after isort just in case they don't agree...
lint: ## lint python sources
lint: \
  lint-isort \
  lint-black \
  lint-flake8 \
  lint-pylint \
  lint-bandit \
  lint-pydocstyle
.PHONY: lint

lint-black: ## lint python sources with black
	@echo 'lint:black started…'
	@$(COMPOSE_RUN_APP) black .
.PHONY: lint-black

lint-flake8: ## lint python sources with flake8
	@echo 'lint:flake8 started…'
	@$(COMPOSE_RUN_APP) flake8
.PHONY: lint-flake8

lint-isort: ## automatically re-arrange python imports
	@echo 'lint:isort started…'
	@$(COMPOSE_RUN_APP) isort --atomic .
.PHONY: lint-isort

lint-pylint: ## lint python sources with pylint
	@echo 'lint:pylint started…'
	@$(COMPOSE_RUN_APP) pylint edx2gift tests
.PHONY: lint-pylint

lint-bandit: ## lint python sources with bandit
	@echo 'lint:bandit started…'
	@$(COMPOSE_RUN_APP) bandit -qr edx2gift
.PHONY: lint-bandit

lint-pydocstyle: ## lint python docstrings with pydocstyle
	@echo 'lint:pydocstyle started…'
	@$(COMPOSE_RUN_APP) pydocstyle
.PHONY: lint-pydocstyle

## -- Tests

test: ## run tests
	bin/pytest
.PHONY: test

# -- Misc
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
