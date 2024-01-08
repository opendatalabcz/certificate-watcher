from dataclasses import dataclass


@dataclass
class PostgreSQLConnectionInfo:
    hostname: str
    port: int
    database: str
    username: str
    password: str
    connect_timeout: int = 4

    def get_connection_args(self):
        return {
            "host": self.hostname,
            "port": self.port,
            "dbname": self.database,
            "user": self.username,
            "password": self.password,
            "connect_timeout": self.connect_timeout,
        }
