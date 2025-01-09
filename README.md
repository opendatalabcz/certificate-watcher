# certificate-watcher

This project is a SSL certificate scanning and phishing prevention tool.
Link to the project GitHub: [certificate-watcher](https://github.com/opendatalabcz/certificate-watcher)

## Getting started

### Prerequisites

- Docker
- Docker-compose
- make

### Running the project

1. Clone the repository
2. Add .env file to the root of the project according to the .env-example and fill it with your own values
   - most importantly fill the `PROJECT_PATH` variable with the absolute path to the root of the project
     - for demo purposes you can use the example values .env-example file
   - you should NOT use example .env-example file in production
3. Run `make build` in the root of the project
   - alternatively you can run `make build-dev` to build each service container separately with file structure for development purposes
4. Run `make run-setup` in the root of the project
   - this will run the setup service to create the database and tables
   - you can also reset database and add test setting with this service
   - change `settings-setup` category in `config/docker-env.cfg` according to desired usage (see below)
   - demo admin user is created with username `admin` and password `admin`
5. Run `make run` script in the root of the project
   - this will run detached containers for each service
   - alternatively you can run `docker-compose up` or `make run-compose` in the root of the project, however it may not run properly due to boot time dependency

## Current schema:

### certificate-stream

Service for inital watching of the certificate stream and its first processing. Currently in test state.


### certificate-processor

Service for processing the certificate stream.

Supports multiple string matching algorithms for detecting suspicious domains.
Currently supports:
- simple string matching (`simple`)
  - looks if checked domain contains any of predefined strings
- levenshtein ratio (`levenshtein`)
  - looks if checked domain is similar to predefined strings according to levenshtein ratio
- domain fuzzing (`fuzzing`)
  - looks if checked domain contains any predefined strings created by fuzzing of legitimate domain
- domain fuzzing with levenshtein ratio (`levensh-fuzz`)
  - looks if checked domain is similar to predefined strings created by fuzzing of legitimate domain according to levenshtein ratio

If new settings are added to the database, the service needs to be restarted to apply them.

### periodic-checker

Service for periodic checking of stored domains for rescanning.

### rabbitmq

RabbitMQ for the certificate stream. Currently running allongside others in docker-compose.
GUI available at `localhost:15672`.

### postgres

Postgres database for storing the certificate stream. Currently running allongside others in docker-compose.

### settings-setup

Service/script for setting up the database and adding test settings.

Demo settings are stored in `services/settings-setup/assets/` and can be added to the database with this service.

The configuration for running is in `config/docker-env.cfg` file in the [settings-setup] category:

- add_demo_settings = true - add demo search_settings
- add_demo_users = true - add demo users
- reset_db = false - delete everything in the database, including users and search_settings

### backend

Service for backend API to manage project

### frontend

Service for GUI to manage project

### nginx

Nginx for routing between services. Currently running allongside others in docker-compose.

## Git workflow

### Commiting

Please use following commit message format:

`[<service>] <message>`

e.g.:

`[certificate-stream] Add readme`

use `[project]` if the commit is not related to a specific service.
