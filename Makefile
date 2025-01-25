SHELL := /bin/sh

.PHONY: local-build
local-build:
	DOCKER_BUILDKIT=1 docker build -t localhost:5001/worker:latest -f ./examples/Dockerfile .
	docker push localhost:5001/worker:latest

.PHONY: deploy
deploy: local-build
	kubectl apply -f ./examples/qworker.yaml

.PHONY: lint
lint:
	poetry run ruff check . --fix

.PHONY: test
test:
	poetry run pytest