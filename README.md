# certificate-watcher

This project is a SSL certificate scanning and phishing prevention tool.


## Current schema:

### certificate-stream

Service for inital watching of the certificate stream and its first processing. Currently in test state.

### certificate-processor

Service for processing the certificate stream. Currently in planning state.

### rabbitmq

RabbitMQ for the certificate stream. Currently running allongside others in docker-compose.

TODO:
- [ ] Add user and password to rabbitmq
- [ ] Add configuration to rabbitmq

### postgres

Postgres database for storing the certificate stream. Currently running allongside others in docker-compose.