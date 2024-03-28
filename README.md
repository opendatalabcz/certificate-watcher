# certificate-watcher

This project is a SSL certificate scanning and phishing prevention tool.

## Getting started

### Prerequisites

- Docker
- Docker-compose
- make

### Running the project

1. Clone the repository
2. Add .env file to the root of the project according to the .env-example and fill it with your own values
   - most importantly fill the `PROJECT_PATH` variable with the absolute path to the root of the project
   - you can and currently should use all other example values for development or test purposes
   - do NOT use example .env file in production
3. Run `make build` in the root of the project
   - alternatively you can run `make build-dev` to build each service container separately with file structure for development purposes
4. Run `make run` script in the root of the project
   - this will run detached containers for each service
   - alternatively you can run `docker-compose up` or `make run-compose` in the root of the project, however it may not run properly due to boot time dependency

## Current schema:

### certificate-stream

Service for inital watching of the certificate stream and its first processing. Currently in test state.

- [ ] Add loggers to certificate-stream

### certificate-processor

Service for processing the certificate stream. Currently in planning state.

Supports multiple string matching algorithms for detecting suspicious domains.
Currently supports:
- simple string matching (`simple`)
  - looks if checked domain contains any of predefined strings

TODO:
- [ ] Add configuration to certificate-processor
- [x] Save suspicioous domains to database - v1
- [x] Add loggers to certificate-processor

### rabbitmq

RabbitMQ for the certificate stream. Currently running allongside others in docker-compose.

TODO:
- [ ] Add user and password to rabbitmq
- [ ] Add configuration to rabbitmq

### postgres

Postgres database for storing the certificate stream. Currently running allongside others in docker-compose.

## Git workflow

### Commiting

Please use following commit message format:

`[<service>] <message>`

e.g.:

`[certificate-stream] Add readme`

use `[project]` if the commit is not related to a specific service.
