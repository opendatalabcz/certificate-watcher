from dataclasses import dataclass


@dataclass
class RabbitMQConnectionInfo:
    hostname: str = None
    port: int = None
    username: str = None
    password: str = None
    virtualhost: str = None
    exchange: str = None
    queue: str = ""
    routing_key: str = ""
    connect_timeout: int = 4

    def get_connection_args(self):
        return {
            "host": self.hostname,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "virtualhost": self.virtualhost,
            "exchange": self.exchange,
            "queue": self.queue,
            "connect_timeout": self.connect_timeout,
        }
