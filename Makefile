.SILENT:
.DEFAULT_GOAL := help

COLOR_RESET = \033[0m
COLOR_COMMAND = \033[36m
COLOR_YELLOW = \033[33m
COLOR_GREEN = \033[32m
COLOR_RED = \033[31m

PROJECT := Flay

## Installs a development environment
install: deploy

## Composes project using docker-compose
deploy:
	#docker-compose -f deployments/docker-compose.yml build --no-cache
	docker-compose -f deployments/docker-compose.yml build
	docker-compose -f deployments/docker-compose.yml down -v
	#docker-compose -f deployments/docker-compose.yml up -d --force-recreate
	docker-compose -f deployments/docker-compose.yml up

## Build the flask-app image
build:
	$(eval $(minikube docker-env))
	docker build . -f deployments/app/Dockerfile --tag flask-app

## Apply the K8s manifests to your cluster
apply: build
	$(eval $(minikube docker-env))
	kubectl apply -f .k8s/

## Port forward the flast app
serve: apply
	kubectl wait --for=condition=available --timeout=600s deployment --all
	kubectl port-forward svc/flask-service 5000:80

## Prints help message
help:
	printf "\n${COLOR_YELLOW}${PROJECT}\n------\n${COLOR_RESET}"
	awk '/^[a-zA-Z\-\_0-9\.%]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "${COLOR_COMMAND}$$ make %s${COLOR_RESET} %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST) | sort
	printf "\n"