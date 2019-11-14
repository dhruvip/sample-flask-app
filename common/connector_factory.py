from .sql_connector import SqlConnector
import os
import logging

logger = logging.getLogger('sample-flask-app')

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls) \
                .__call__(*args, **kwargs)
        return cls._instances[cls]

class ConnectorFactory(metaclass=Singleton):

    def __init__(self, config_obj):
        self.config_obj = config_obj
        self._factory = {}

    def make_db_connector(self):
        if 'sqlite_conn' in self._factory:
            return self._factory['sqlite_conn']
        DATABASE = './config/{}.db'.format(self.config_obj['db']['sqlite_path'])
        conn = SqlConnector(DATABASE)
        self._factory['sqlite_conn'] = conn
        return conn