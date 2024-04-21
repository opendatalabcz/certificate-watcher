from dataclasses import dataclass

NOTE_DB_MAPPING = {
    "SCRAPE_ERROR": "Website scrape error",
    "IMG_DOWNLOAD_ERROR": "Img download error",
    "NO_STATIC_IMAGES": "No static images found",
}

NOTE_DB_MAPPING_REVERSE = {v: k for k, v in NOTE_DB_MAPPING.items()}


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
