#!/bin/bash

docker compose up -d rabbitmq

# Wait for RabbitMQ to boot up
sleep 15

# Start all other services
docker compose up -d certificate-stream
docker compose up -d certificate-processor

echo "All services are up and running"