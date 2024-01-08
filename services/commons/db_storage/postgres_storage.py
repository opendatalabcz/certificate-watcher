import os

import psycopg2

from .abstract_storage import AbstractStorage
from .utils import PostgreSQLConnectionInfo


class PostgresStorage(AbstractStorage):
    def __init__(self, database_connection_info: PostgreSQLConnectionInfo, permanent_connection: bool = True):
        super().__init__()
        self.database_connection_info = database_connection_info
        self.permanent_connection = permanent_connection

        self.connection = self.__create_connection(self.database_connection_info)
        self.cursor = self.connection.cursor()

        self.autocommit = True

    def __create_connection(self, database_connection_info):
        connection = psycopg2.connect(**database_connection_info.get_connection_args())
        print(f"Created connection for db: {self.database_connection_info.database} on {self.database_connection_info.hostname}")
        return connection

    def __close_connection(self):
        self.connection.close()
        print(f"Closed connection for db: {self.database_connection_info.database} on {self.database_connection_info.hostname}")

    def __del__(self):
        self.__close_connection()

    def rollback(self):
        self.connection.rollback()

    def commit(self):
        self.connection.commit()

    def execute(self, query, params: tuple = None):
        try:
            self.cursor.execute(query, params)
            if self.autocommit is True:
                self.commit()
        except (psycopg2.OperationalError, psycopg2.InterfaceError, psycopg2.InternalError) as e:
            print(f"Lost PostgreSQL connection, sick of it => Goodbye! {e}", flush=True)
            os._exit(3)
        except psycopg2.Error as e:
            self.rollback()

            print(f"Postgres error: {e}, query:{query}")
            raise Exception(f"Postgres error: {e}") from e
