import pika

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
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()
        self.is_active = False

    def send(self, data):
        self.channel.basic_publish(exchange=self.exchange_name, routing_key=self.routing_key, body=data)

    def receive_single_frame(self):
        if not self.is_active or self.connection.is_closed or self.channel.is_closed:
            self._reconnect()
        method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=True)
        if method_frame:
            return body.decode("utf-8")
        return None

    def receive_multiple_frames(self, callback):
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def _connect(self):
        credentials = pika.PlainCredentials(self.connection_parameters.username, self.connection_parameters.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.connection_parameters.hostname,
                credentials=credentials,
            )
        )
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name, exchange_type="direct")

    def setup_producer(self):
        self._connect()
        self.is_active = True

    def setup_consumer(self):
        self._connect()

        queue_name = self.connection_parameters.queue
        try:
            self.channel.queue_declare(queue=queue_name, passive=True)
            self.logger.info(f"Queue {queue_name} exists")
        except pika.exceptions.ChannelClosedByBroker:
            self.logger.info(f"Queue {queue_name} does not exist, creating it")
            self._connect()
            self.channel.queue_declare(queue=queue_name, exclusive=False)
        self.queue_name = queue_name
        self.channel.queue_bind(exchange=self.exchange_name, queue=self.queue_name, routing_key=self.routing_key)

        self.is_active = True

    def _reconnect(self):
        self._close_connections()
        if self.queue_name:
            self.setup_consumer()
        else:
            self.setup_producer()

    def __del__(self):
        self._close_connections()
        self.logger.info("Closed connections for RabbitMQStreamHandler")
