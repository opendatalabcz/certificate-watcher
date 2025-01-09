#!/bin/bash

docker compose up -d rabbitmq
docker compose up -d postgres

# Wait for RabbitMQ to boot up
echo "Waiting for RabbitMQ and Postgresql to boot up..."
sleep 15


# Start all other services
docker compose up -d certificate-stream
docker compose up -d certificate-processor-domain-str-simple
docker compose up -d certificate-processor-domain-images
docker compose up -d periodic-scrape-checker

docker compose up -d backend
docker compose up -d frontend

docker compose up -d nginx

echo "All services are up and running"