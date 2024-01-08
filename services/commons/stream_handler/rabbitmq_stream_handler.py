import pika

from .abstract_stream_handler import AbstractStreamHandler


class RabbitMQStreamHandler(AbstractStreamHandler):
    def __init__(self, connection_parameters, queue_name):
        super().__init__()
        self.connection_parameters = connection_parameters
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.is_active = False
        self._connect()

    def _close_connections(self):
        self.channel.close()
        self.connection.close()
        self.is_active = False

    def send(self, data):
        self.channel.basic_publish(exchange="", routing_key=self.queue_name, body=data)

    def receive_single_frame(self):
        method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=True)
        if method_frame:
            return body.decode("utf-8")
        return None

    def receive_multiple_frames(self, callback):
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def _connect(self):
        credentials = pika.PlainCredentials(self.connection_parameters["username"], self.connection_parameters["password"])
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.connection_parameters["hostname"],
                credentials=credentials,
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        self.is_active = True

    def _reconnect(self):
        self._close_connections()
        self._connect()

    def __del__(self):
        self._close_connections()
        print("Closed connections for RabbitMQStreamHandler")
