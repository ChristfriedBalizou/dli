from tabulate.tabulate import tabulate

import subprocess
import sys
import os
import re
import csv
import io
import json

class Adapter(object):

    def  __init__(self,
            server=None,
            port=None,
            user=None,
            connection_cmd=None,
            cmd=None,
            test_query=None,
            database=None,
            error_regex=None,
            password=None,
            fmt="sql"):

        '''
        The init function contain the connection parameters
        to initiate the database instance.
        '''

        self.server = server
        self.port = port
        self.user = user
        self.database = database
        self.password = password
        self.cmd = cmd
        self.test_query = test_query
        self.connection_cmd = connection_cmd
        self.error_regex=error_regex
        self.fmt = fmt
        self.__connection__ = None


    def connect(self, test=True):
        '''
        Open a connection to the database.
        '''

        if not self.__program_exist__():
            raise Exception("Command %s is not installed. the connection failed."
                    % self.cmd)

        self.__connection__ = subprocess.Popen(
            self.connection_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        if test is True:
            try:
                self.__connection__.communicate(input=self.test_query)
                print 'Connection openned successfuly.'
            except Exception:
                raise


    def execute(self, query):
        '''
        Execute run sql query commande whithout return
        results.
        '''
        try:
            self.connect(test=False)
        except:
            pass


    def select(self, query=None, fmt=None):
        '''
        Runs command and "always" return dictionary array
        '''
        self.connect(test=False)



    def close(self):
        '''
        Close database connection
        '''
        self.__connection__.communicate(input="quit")
        self.__connection__.kill()
        print "Connection closed successfuly."
        self.__connection__ = None


    def tables(self, name=None, fmt=None):
        '''
        List all tables. If name is given return the
        requested or None
        '''

        self.connect(test=False)


    def description(self, table_name=None, fmt=None):
        '''
        List all table with descriptions
        (table => fields => column : type)
        If table_name is given only specified
        will be listed
        '''

        self.connect(test=False)


    def __program_exist__(self):

        if self.cmd is None:
            return True

        try:
            for cmd in self.cmd:
                with open(os.devnull, 'w') as devnull:
                    subprocess.call([cmd], stderr=devnull)
                    return True
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                return False
        return True

    def __runsql__(self, sql, fmt=None):
        pass


    def has_error(self, output):
        '''
        Check if response from sql server came with error
        '''
        if self.error_regex is not None:
            if re.search(self.error_regex, output) is not None:
                return True

        return False


    def to_response(self, output, fmt=None):
        '''
        Marshall csv to dictionary
        '''
        if fmt == "csv":
            return output.replace("\t", ",")

        docs = []
        if fmt == "json":
            return self.__to_dict__(output)

        if fmt == "sql":
            return self.__to_table__(output)

        if fmt is None:
            if self.fmt is "json":
                return self.__to_dict__(output)
            return self.__to_table__(output)


    def __to_table__(self, infile):
        reader = csv.reader(infile, delimiter='\t')
        headers = reader.next()
        return tabulate(reader, headers, tablefmt="orgtbl")


    def __to_dict__(self, text):
        docs = []
        for row in csv.DictReader(text.splitlines(), delimiter='\t'):
            doc = {key: value for key, value in row.items()}
            docs.append(doc)

        return json.dumps(docs, indent=4)
