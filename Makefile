# Makefile

build-dev:
	@echo "Building services..."
	@cd services/certificate-stream && make build
	@cd services/certificate-processor && make build

build:
	@echo "Building services..."
	@docker compose build

run:
	@echo "Running script..."
	@./run.sh

run-setup:
	@echo "Running setup services..."
	@docker compose up -d settings-setup

run-compose:
	@echo "Running Docker Compose..."
	@docker compose up

all: build run