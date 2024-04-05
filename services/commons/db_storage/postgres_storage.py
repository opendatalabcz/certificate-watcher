import os

import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from .abstract_storage import AbstractStorage
from .models import Base
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
        self.logger.info(f"Created connection for db: {database_connection_info.database} on {database_connection_info.hostname}")
        return connection

    def __close_connection(self):
        self.connection.close()
        self.logger.info(f"Closed connection for db: {self.database_connection_info.database} on {self.database_connection_info.hostname}")

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
            self.logger.error(f"Lost PostgreSQL connection, sick of it => Goodbye! {e}")
            os._exit(3)
        except psycopg2.Error as e:
            self.rollback()
            self.logger.error(f"Postgres error: {e}, query:{query}")
            raise Exception(f"Postgres error: {e}") from e


class SqlAlchemyStorage(AbstractStorage):
    def __init__(self, database_connection_info: PostgreSQLConnectionInfo):
        super().__init__()
        self.database_connection_info = database_connection_info

        self.engine = self.__create_connection_engine(self.__create_connection_string(self.database_connection_info))
        self.persistent_sessions = None
        self.__init_tables()

    @staticmethod
    def __create_connection_string(database_connection_info):
        return f"postgresql+psycopg2://{database_connection_info.username}:{database_connection_info.password}@{database_connection_info.hostname}:{database_connection_info.port}/{database_connection_info.database}"

    @staticmethod
    def __create_connection_engine(connection_string):
        return create_engine(connection_string)

    def reset_db_schema(self, schema="public"):
        self.logger.info("Dropping all tables")

        with self.engine.connect() as conn:
            # Start a transaction
            trans = conn.begin()

            try:
                # Drop the schema, cascading to drop all objects within it
                conn.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
                # Recreate the schema
                conn.execute(text(f"CREATE SCHEMA {schema}"))
                trans.commit()
                self.logger.info(f"Schema '{schema}' has been reset.")
            except Exception as e:
                self.logger.error(f"An error occurred: {e}")
                trans.rollback()

        self.__init_tables()

    def __init_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return sessionmaker(bind=self.engine)()

    def get(self, model, **kwargs):
        with self.get_session() as session:
            return session.query(model).filter_by(**kwargs).all()

    def add(self, items: list, prepared_session=None):
        session = prepared_session if prepared_session else self.get_session()
        session.add_all(items)
        session.commit()

        self.logger.info(f"Added {len(items)} items to the database")

        if not prepared_session:
            session.close()
