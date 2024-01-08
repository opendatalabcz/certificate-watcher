from dataclasses import dataclass


@dataclass
class RabbitMQConnectionInfo:
    hostname: str
    port: int
    username: str
    password: str
    virtualhost: str
    connect_timeout: int = 4

    def get_connection_args(self):
        return {
            "host": self.hostname,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "virtualhost": self.virtualhost,
            "connect_timeout": self.connect_timeout,
        }
