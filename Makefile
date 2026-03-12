.PHONY: help up down clean build rebuild

help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: \033[36mmake <target>\033[0m\n\nAwailable targets:\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-49s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

up: ## Start Docker containers in detached mode
	docker compose up -d

down: ## Stop Docker containers
	docker compose down

clean: ## Stop Docker containers and remove volumes
	docker compose down -v

build: ## Build Docker images
	docker compose build

rebuild: ## Build Docker images without using cache
	docker compose build  --no-cache


.PHONY: test
test: ## Run tests in Docker: make test
	docker compose exec api pytest $(path)

.PHONY: test-v
test-v: ## Run tests in Docker in verbose mode: make test-v path=tests/test.py::test_case
	docker compose exec api pytest -v $(path)

.PHONY: _ensure-file-arg
_ensure-file-arg:
ifndef file
	$(error 'file' argument is not defined)
endif
.PHONY: db-dump
db-dump: _ensure-file-arg ## Dump DB from Docker to file: make db-dump file=db.dump
	docker exec -i db pg_dump -U postgres -d todo -F c > $(file)

.PHONY: db-restore
db-restore: _ensure-file-arg ## Restore DB in Docker from file: make db-restore file=db.dump
	docker exec -i db pg_restore -U postgres -d todo --clean --if-exists < $(file)
