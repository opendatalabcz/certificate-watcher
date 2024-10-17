import time

import pika
from pika.exceptions import (
    AMQPConnectionError,
    ChannelClosedByBroker,
    ConnectionClosedByBroker,
    ConnectionWrongStateError,
    StreamLostError,
)

from .abstract_stream_handler import AbstractStreamHandler
from .utils import RabbitMQConnectionInfo


class RabbitMQStreamHandler(AbstractStreamHandler):
    def __init__(self, connection_parameters: RabbitMQConnectionInfo):
        super().__init__()
        self.connection_parameters = connection_parameters
        self.exchange_name = self.connection_parameters.exchange
        self.queue_name = None
        self.connection = None
        self.channel = None
        self.routing_key = self.connection_parameters.routing_key

    def _close_connections(self):
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
        except Exception as e:
            self.logger.error(f"Error closing channel: {e}")
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
        except Exception as e:
            self.logger.error(f"Error closing connection: {e}")
        self.is_active = False

    def send(self, data):
        try:
            if not self.channel or self.channel.is_closed:
                self._reconnect()
            self.channel.basic_publish(exchange=self.exchange_name, routing_key=self.routing_key, body=data)
        except (AMQPConnectionError, StreamLostError, ConnectionClosedByBroker, ChannelClosedByBroker, ConnectionWrongStateError) as e:
            self.logger.error(f"Error sending message: {e}")
            self._reconnect()
            try:
                self.channel.basic_publish(exchange=self.exchange_name, routing_key=self.routing_key, body=data)
            except Exception as e:
                self.logger.error(f"Error sending message: {e}")
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            raise Exception from e

    def receive_single_frame(self):
        try:
            if not self.is_active or self.connection.is_closed or self.channel.is_closed:
                self._reconnect()
            method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=True)
            if method_frame:
                return body.decode("utf-8")
            return None
        except (AMQPConnectionError, StreamLostError, ConnectionClosedByBroker, ChannelClosedByBroker, ConnectionWrongStateError) as e:
            self.logger.error(f"Error receiving message: {e}")
            self._reconnect()
            return None
        except Exception as e:
            self.logger.error(f"Error receiving message: {e}")
            raise Exception from e

    def receive_multiple_frames(self, callback):
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def _connect(self):
        credentials = pika.PlainCredentials(self.connection_parameters.username, self.connection_parameters.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.connection_parameters.hostname,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )
        )
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type="direct", durable=True)
        self.is_active = True

    def _reconnect(self):
        self._close_connections()
        retry_delay = 5
        while True:
            try:
                self.logger.info("Attempting to reconnect to RabbitMQ...")
                self._connect()
                self.logger.info("Reconnected to RabbitMQ")
                break
            except AMQPConnectionError as e:
                self.logger.error(f"Connection error: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

    def setup_producer(self):
        try:
            self._connect()
        except Exception as e:
            self.logger.error(f"Error connecting to RabbitMQ: {e}")
            self._reconnect()

    def setup_consumer(self):
        self._connect()

        try:
            self.channel.queue_declare(queue=self.connection_parameters.queue, durable=True)
            self.logger.info(f"Queue {self.connection_parameters.queue} exists")
        except Exception as e:
            self.logger.error(f"Error declaring queue {self.connection_parameters.queue}: {e}")
            self._reconnect()
            # Retry after reconnecting
            self.channel.queue_declare(queue=self.connection_parameters.queue, durable=True)
        self.queue_name = self.connection_parameters.queue
        self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=self.routing_key)

    def __del__(self):
        try:
            self._close_connections()
            self.logger.info("Closed connections for RabbitMQStreamHandler")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
