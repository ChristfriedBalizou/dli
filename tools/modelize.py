'''
 modelize.py process a given directory to extract comprehensive
 information to build dot template.

 This require a well describ directory.
'''

import os

from collections import defaultdict


def directory_walk(directory, docs, table_list):

    '''
    directory_walk and extract table with their fields
    '''

    for root, dirs, files in os.walk(directory):

        for f in files:
            if len(table_list) != 0 and f not in table_list:
                continue
            full_path = os.path.join(root, f)
            table_name = os.path.basename(full_path)
            dirpath = os.path.dirname(full_path)
            db_name = os.path.basename(dirpath)

            with open(full_path) as table_file:
                fields = table_file.read().splitlines()
                docs[db_name].update({table_name: set(fields)})

        for d in dirs:
            directory_walk(os.path.join(root, d), docs, table_list)


def pair_table(table_list, tab, tables_doc, docs):

    '''
    Group table list by pairs discarding
    reverse on same relation
    '''

    for t in table_list:
        if (t, tab,) in docs \
                or (tab, t,) in docs:
                    continue

        fields = [{"left": x,
                   "right": x,
                   "is_deleted": False,
                   "relation_type": None}
                   for x in (tables_doc[t] & tables_doc[tab])]

        docs[(tab, t,)] = {"a": tab,
                           "b": t,
                           "fields": fields}


class Modelize(object):

    def __init__(self,
                 directory=None,
                 table_list=[],
                 draw_relations=False,
                 relation_criterion=None):
        '''
        Initialize and load data
        '''

        self.directory = os.path.expanduser(directory)
        self.table_list = table_list
        self.relation_criterion = relation_criterion
        self.draw_relations = draw_relations

        if not os.path.exists(self.directory):
            print "Can't open directory %s. File not found" % directory
            return None

        # load all tables peer database with their columns
        self.docs = defaultdict(dict)
        self.load_tables_peer_database()


    def load_tables_peer_database(self):
        '''
        Using os.walk we recurcively go through
        directories and read tables files.

        Each directory is a database
        '''

        directory_walk(self.directory, self.docs, self.table_list)


    def dot_relations(self):

        '''
        dot_relations return a dot relational
        text format to be transform to dot file
        '''

        relations = {}

        for _, table_doc in self.docs.items():
            table_list = table_doc.keys()

            for tab in table_list:
                pair_table(filter(lambda x: x != tab, table_list),
                           tab,
                           table_doc,
                           relations)

        return relations.values()


    def dot(self):

        '''
        dot return a list of table with their columns peer database
        '''

        results = []

        for db, table_list in self.docs.items():

            table_doc = [{"name": name,
                          "fields": list(fields)}
                         for name, fields in table_list.items()]

            results.append({"name" : db,
                            "tables" : table_doc})

        return results


    def table_skeleton(self, name=None):

        '''
        table_skeleton return a table with columns
        e.i: {table_a: [cola, colb, ..., coln]}
        '''

        for _, tables_doc in self.docs.items():

            tab_doc = tables_doc.get(name)

            if tab_doc is None:
                continue

            return {name: tab_doc.values()}

        return None


    def statistics(self):

        '''
        statistics return count of all columns and tables
        '''

        #FIXME show statistic peer database
        for _, tables_doc in self.docs.items():
            docs = {"tables_number": len(tables_doc),
                    "columns_number": len(tables_doc.values())}

        return docs


    def list_table(self):

        '''
        list_table return a table list peer databasies
        '''

        results = []

        #FIXME show table list peer database
        for _, tables_doc in self.docs.items():
            results += tables_doc.keys()

        return sorted(results)


    def list_fields(self):

        '''
        list_fields return all fields peer database
        in sort -u mode
        '''

        results = set()

        #FIXME show table list peer database
        for _, tables_doc in self.docs.items():
            results |= tables_doc.values()

        return sorted(results)
