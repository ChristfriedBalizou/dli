'''
Kruskal's is a solution implemented to avoid
cyclic relations in the generated graph base on
Union-find algorithm

Using edge ranking we will avoid human intervention
to validate relations between table.

First we will count occurence of each columns.
Givin it a rank we will create a wilcard, those
will be the columns use to link tables.

The sum of columns rank will give a weight to
the corresponding table. The link between tables will be done
by max weight linking.

https://en.wikipedia.org/wiki/Kruskal%27s_algorithm
'''

from tools.modelize import Modelize

from collections import defaultdict
from datetime import datetime

import os
import sys
import json



CURRENT_DIRECTORY = os.path.dirname(os.path.relpath(__file__))
DB_SCHEMA_DIRECTORY = os.path.join(CURRENT_DIRECTORY, '..', 'DB_SCHEMA')
COLUMNS_WEIGHT_FILE = 'columns.libd'
KEYS_FILE = 'keys.libd'

class Kruskal(object):

    def __init__(self):

        '''
        Try to load precomputed columns weight file
        if not exists create it.
        '''

        self.weights = {}
        self.keys = {}

        self.up = []
        self.rank = []

        model = Modelize(directory=DB_SCHEMA_DIRECTORY)

        for db, tables_doc in model.docs.items():

            db_directory = os.path.join(DB_SCHEMA_DIRECTORY, db)
            weight_file = os.path.join(db_directory, COLUMNS_WEIGHT_FILE)
            keys_file = os.path.join(db_directory, KEYS_FILE)

            self.keys[db] = []

            if os.path.exists(weight_file):
                gmtime = os.path.getmtime(weight_file)
                # If weight file is a month old delete it
                if datetime.now().month != \
                        datetime.fromtimestamp(gmtime).month:
                    os.remove(weight_file)

            if not os.path.exists(weight_file):
                # If weight file is missing create it
                docs = defaultdict(int)

                for fields in tables_doc.values():
                    for field in fields:
                        docs[field] += 1

                with open(weight_file, 'wb') as writer:
                    json.dump(dict(docs), writer)

            # Load weight file
            with open(weight_file) as reader:
                self.weights[db] = json.load(reader)

            # Load keys file
            if os.path.exists(keys_file):
                with open(keys_file) as keys_reader:
                    self.keys[db] = keys_reader.read().splitlines()


    def span_tree(self, db_name, relations):

        if len(relations) == 0:
            return []

        table_weight = defaultdict(int)
        weights = self.weights[db_name]
        keys = set(self.keys[db_name])
        table_list = set()

        for k, rel in relations.items():

            left_table, right_table = k

            table_list |= set(k)

            for field in rel['fields']:

                left = field['left']
                right = field['right']

                # Discard unlisted fields if listed are given
                if len(keys) > 0:
                    if len(set(left.split('_')) & keys) == 0 \
                            or len(set(right.split('_')) & keys) == 0:
                        rel['fields'].remove(field)
                        continue

                key = (left_table, right_table,)
                table_weight[key] += weights[left] + weights[right]


        # Kruskal table list
        table_list = list(table_list)
        rels = sorted([(v, k,) for k, v in table_weight.iteritems()],
                      reverse=True)

        self.up = list(range(len(table_list)))
        self.rank = [0] * len(table_list)

        table_list_doc = {k: v for v, k in enumerate(table_list)}

        for _, k in rels:
            left, right = k
            left_index = table_list_doc[left]
            right_index = table_list_doc[right]
            self.union(left_index, right_index)

        outdoc = {}

        for i, v in enumerate(self.up):

            rel = None

            if (table_list[i], table_list[v],) in relations:
                rel = relations[(table_list[i], table_list[v],)]
            if (table_list[v], table_list[i],) in relations:
                rel = relations[(table_list[v], table_list[i],)]

            if rel is None:
                continue

            if (table_list[i], table_list[v],) in outdoc:
                continue

            outdoc[(table_list[i], table_list[v],)] = rel


        return outdoc.values()


    def find(self, x):

        if self.up[x] == x:
            return x
        else:
            self.up[x] = self.find(self.up[x])
            return self.up[x]


    def union(self, x, y):

        repr_x = self.find(x)
        repr_y = self.find(y)

        if repr_x == repr_y:
            return False
        if self.rank[repr_x] == self.rank[repr_y]:
            self.rank[repr_x] += 1
            self.up[repr_y] = repr_x
        elif self.rank[repr_x] > self.rank[repr_y]:
            self.up[repr_y] = repr_x
        else:
            self.up[repr_x] = repr_y
        return True

