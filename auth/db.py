from adapters.sybase import Sybase

import os
import ConfigParser

DRIVERS = {
        'sybase': Sybase,
}



class Database(object):

    def __init__(self, *args, **kwargs):

        if 'config_path' in kwargs:
            config_path = kwargs.pop('config_path')
            section = kwargs.pop('section')
            cfg = self.load_config(section, path=config_path)
            database_type = cfg.pop('type')
        else:
            cfg = kwargs

        self.db = DRIVERS[database_type](**cfg)


    def connect(self):
        self.db.connect()


    def close(self):
        self.db.close()


    def select(self, query, fmt=None):
        return self.db.select(query, fmt=fmt)


    def execute(self, query):
        self.db.execute(query)


    def tables(self, name=None, fmt=None):
        return self.db.tables(name=name, fmt=fmt)


    def description(self, table_name=None, fmt=None):
        return self.db.description(table_name=table_name, fmt=fmt)


    def load_config(self, database, path=None):

        if path is None:
            raise IOError("Config file path 'None' not found")

        filepath = os.path.expanduser(path)

        if not os.path.exists(filepath):
            raise Exception("Config file %s not found." % path)
        config = ConfigParser.ConfigParser()
        config.read(filepath)
        return dict(config.items(database))


