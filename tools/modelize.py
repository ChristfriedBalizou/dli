'''
 modelize.py process a given directory to extract comprehensive
 information to build dot template.

 This require a well describ directory.
'''

import sys
import os
import re

from collections import defaultdict

class Modelize(object):

    def __init__(self,
            directory=None,
            table_list=[],
            draw_relations=False,
            relation_criterion=None):

        self.docs = defaultdict(set)
        self.relations = []
        self.__relations_pair__ = defaultdict(set)
        self.__fields__ = defaultdict(set)
        self.__tables__ = {}
        self.__table_description__ = {}
        self.table_list = table_list
        self.relation_criterion = relation_criterion
        self.draw_relations = draw_relations

        self.directory = os.path.expanduser(directory)


        if not os.path.exists(self.directory):
            print "Can't open directory %s. File not found" % directory
            return None

        self.__extract_tables__(self.directory)


    def dot_relations(self):

        if self.draw_relations is False:
            return []

        if len(self.relations) > 0:
            return self.relations

        self.__make_relations__()

        for k, v in self.__relations_pair__.items():
            a, b = k
            self.relations.append({"a": a, "b": b, "fields": list(v)})

        return self.relations


    def dot(self):

        results = []

        self.__process__()

        for db, table_list in self.docs.items():
            results.append({ "name" : db, "tables" : table_list })

        return results


    def statistics(self):

        self.__process__()
        docs = {"tables_number": len(self.__tables__),
                "columns_number": len(self.__fields__)}

        if len(self.table_list) == 0:
            return docs


        docs["tables_number"] = len(self.table_list)
        docs["columns_number"] = 0

        for _, tabs in self.__fields__.items():
            for t in self.table_list:
                if not t in tabs:
                    continue
                docs["columns_number"] = docs["columns_number"] + 1

        return docs


    def __extract_tables__(self, directory):
        for root, dirs, files in os.walk(directory):
            for f in files:
                if len(self.table_list) != 0 and f not in self.table_list:
                    continue

                full_path = os.path.join(root, f)
                self.__tables__[os.path.basename(full_path)] = full_path

            for d in dirs:
                self.__extract_tables__(os.path.join(root, d))


    def list_table(self):
        return sorted(self.tables().keys())


    def tables(self):
        return self.__tables__


    def __make_relations__(self):

        for field, table_list in self.__fields__.items():
            # Do not create link with REC* columns
            # Which are identified as Date field
            if self.relation_criterion is not None\
                and re.search(self.relation_criterion, field):
                continue

            for t in self.__tables__:

                if len(self.table_list) != 0 and t not in self.table_list:
                    continue

                if not t in table_list:
                    continue

                self.__regroup__(field, t, table_list)


    def __regroup__(self, field, table, table_list):

        for t in table_list:
            # Drop reverse key combination
            if self.__relations_pair__.get((t, table,), None) is not None:
                continue
            # Do not create link on same table
            if t == table:
                continue

            self.__relations_pair__[(table, t,)].add(field)


    def __process__(self):

        for table, path in self.__tables__.items():

            if len(self.table_list) != 0 and table not in self.table_list:
                continue

            dirpath = os.path.dirname(path)
            db_name = os.path.basename(dirpath)

            if not db_name in self.docs:
                self.docs[db_name] = []

            table = { "name": table, "fields": self.extract_fields(path) }

            self.docs[db_name].append(table)


    def extract_fields(self, file_path):

        table_name = os.path.basename(file_path)

        with open(file_path) as f:
            lines = f.read().splitlines()

            for l in lines:
                self.__fields__[l].add(table_name)

        return lines
