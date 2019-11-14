import os
import traceback
from flask import g
import sqlite3
import logging 

logger = logging.getLogger('sample-flask-app')

class SqlConnector:
    def __init__(self, config):
        self.config = config
        self.db_conn = None

    @staticmethod
    def get_db_conn(config):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(config)
        return db


    # def is_conn_open(self):
    #     if self.db_conn is not None:
    #         return True
    #     return False
    
    # def open_db_conn(self):
    #     if self.is_conn_open():
    #         logger.debug('DB connection already opened')
    #         return
        
    #     db = getattr(g, '_database', None)
    #     if db is None:
    #         db = g._database = sqlite3.connect(self.config)
    #     self.db_conn = db
    #     logger.debug('database connection open')

    # def close_db_conn(self):
    #     if self.is_conn_open():
    #         self.db_conn.close()
    #         self.db_conn = None
    #         logger.debug('database connection closed')
    #     else:
    #         logger.debug('database already close')

    # def open(self):
    #     self.open_db_conn()

    # def close(self):
    #     self.close_db_conn()

    # def __enter__(self):
    #     self.open()
    #     return self

    # def __exit__(self, exc_type, exc_value, tb):
    #     if exc_type is not None:
    #         traceback.print_exception(exc_type, exc_value, tb)
    #         # return False # uncomment to pass exception through
    #     self.close()
    #     return True

    def select(self, query_str):
        response = list()
        try:
            sqliteConnection = SqlConnector.get_db_conn(self.config)
            cursor = sqliteConnection.cursor()
            logger.debug("Connected to SQLite")

            sqlite_select_query = query_str
            cursor.execute(sqlite_select_query)
            records = cursor.fetchall()
            response =  records
            cursor.close()

        except sqlite3.Error as error:
            logger.debug("Failed to read data from sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                logger.debug("The SQLite connection is closed")

        return response

    def insert(self, query_str, values=None):
        try:
            sqliteConnection = SqlConnector.get_db_conn(self.config)
            cursor = sqliteConnection.cursor()
            logger.debug("Connected to SQLite")

            sqlite_insert_query = query_str
            if values is not None:
                sqlite_insert_query = sqlite_insert_query.format(values)
            count = cursor.execute(sqlite_insert_query)
            sqliteConnection.commit()
            logger.debug("Record inserted successfully ")
            cursor.close()
            return True

        except sqlite3.Error as error:
            logger.debug("Failed to insert data into sqlite table", error)
            return False
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                logger.debug("The SQLite connection is closed")


    def update(self, query_str):
        try:
            sqliteConnection = SqlConnector.get_db_conn(self.config)
            cursor = sqliteConnection.cursor()
            logger.debug("Connected to SQLite")

            sqlite_insert_query = query_str
            count = cursor.execute(sqlite_insert_query)
            sqliteConnection.commit()
            logger.debug("Record updated successfully ")
            cursor.close()
            return True

        except sqlite3.Error as error:
            logger.debug("Failed to update data into sqlite table", error)
            return False
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                logger.debug("The SQLite connection is closed")
