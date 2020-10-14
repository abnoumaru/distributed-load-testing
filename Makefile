.DEFAULT_GOAL := help

## TODO: fix your environment
NAME="abnoumaru/locust"

########################
# docker build
########################
.PHONY: docker.build.locust-image
docker.build.locust-image: ## Build locust docker image 
	@cd ./locust-image; docker build -t $(NAME) .

########################
# test locust in local (docker-compose)
########################
docker.compose.up: ## Create/Recreate locust cluster in local
	@docker-compose -p locust up -d

docker.compose.logs: ## View locust cluster logs
	@docker-compose -p locust logs

docker.compose.stop: ## Shutdown locust cluster in local
	@docker-compose -p locust stop

open.webconsole.local: ## Open web console in local
	@open http://localhost:8089

#############################
# help
#############################
help: ## Print help
	@echo "Usage: make [SUB_COMMAND]"
	@echo ""
	@echo "Command list:"
	@echo ""
	@printf "\033[36m%-30s\033[0m %-50s %s\n" "[Sub command]" "[Description]"
	@grep -E '^[a-zA-Z_-]+.*?:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
