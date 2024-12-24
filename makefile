SHELL := /bin/sh

.PHONY: local-build
local-build:
	DOCKER_BUILDKIT=1 docker build -t localhost:5001/worker:0.0.1 -f ./examples/Dockerfile .
	docker push localhost:5001/worker:0.0.1

.PHONY: deploy
deploy:
	kubectl apply -f ./examples/qworker.yaml
