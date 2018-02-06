from model.models import (
        TableModel,
        ColumnModel,
        RelationModel,
        User,
        Meta,
        DBsession
        )

from tools.modelize import Modelize
from defs import compute_relations, get_relations_from_db
from multiprocessing import Pool
from sqlalchemy import func
from sqlalchemy import or_

import sys
import os
import json


def search_table(model, query):
    sess = DBsession()

    docs = {"tag": "tables", "res": []}

    # find matching table
    table_res = [x for x in model.list_table() if x.lower() == query.lower()]

    try:
        for t in table_res:
            meta = (sess.query(Meta)
                        .filter(Meta.meta_type=='description',
                                Meta.meta_table.has(name=t))
                        .first())

            if meta is not None:
                t = meta.json()

            docs["res"].append(t)
    finally:
        sess.close()

    return docs



def search_column(model, query):
    sess = DBsession()

    docs = {"tag": "columns", "res": []}

    # find matching column
    column_res = [x for x in model.list_fields() if x.lower() == query.lower()]

    try:
        for c in column_res:
            meta = (sess.query(Meta)
                        .filter(Meta.meta_type=='description',
                                Meta.meta_column.has(name=c))
                        .first())

            if meta is not None:
                c = meta.json()

            docs["res"].append(c)
    finally:
        sess.close()

    return docs


def search_relation(model, query):
    sess = DBsession()

    docs = {"tag": "relations", "res": []}
    return None

    # get possible related from database and automaticaly
    rels = (sess.query(RelationModel)
            .filter(or_(RelationModel.tablel.has(func.lower(TableModel.name) == query.lower()),
                        RelationModel.tabler.has(func.lower(TableModel.name) == query.lower()),
                        RelationModel.columnl.has(func.lower(TableModel.name) == query.lower()),
                        RelationModel.columnr.has(func.lower(TableModel.name) == query.lower())))
            .distinct()
            .all())

    try:
        docs["res"] = compute_relations(model.dot_relations(),
                                              rels,
                                              remove_deleted=True)
    finally:
        sess.close()

    return docs


def search_meta(model, query):
    sess = DBsession()

    docs = []
    relations = {}
    table_list = []
    column_list = set()

    query = query.replace("''", "")

    # fetch in metadata
    metadatas = (sess.query(Meta)
                 .distinct()
                 .filter(or_(
                     Meta.description.ilike("%{}%".format(query)),
                     Meta.meta_table.has(func.lower(TableModel.name)==query.lower()),
                     Meta.meta_column.has(func.lower(ColumnModel.name)==query.lower())
                     ))
                 .all())

    try:
        for meta in metadatas:

            if meta.meta_type == "related":
                rels = (sess.query(RelationModel)
                        .filter(or_(RelationModel.tablel==meta.meta_table,
                                    RelationModel.tabler==meta.meta_table))
                        .distinct()
                        .all())

                key = (meta.meta_table,)

                for r in rels:
                    obj = {"description": description_or_query(sess,
                                                               meta.meta_table,
                                                               "tag",
                                                               query),
                           "link": [r.tablel.name, r.tabler.name],
                           "user": meta.user.json()}

                    if relations.get(key) is None:
                        relations[key] = obj
                    else:
                        relations.get(key)['link'] = list(set(relations.get(key)['link']) |
                                                          set([r.tablel.name, r.tabler.name]))

            if meta.meta_type == "description":
                res = (sess.query(TableModel)
                       .filter(func.lower(TableModel.name) == query.lower())
                       .all())
                for r in res:
                    obj = r.json()
                    if obj in table_list:
                        continue
                    table_list.append(obj)

            if meta.meta_type in ["tag", "other"]:

                # Set originator user
                user = meta.user
                if user is None:
                    user = User(username="lbdbot",
                                first_name="lbDbot",
                                last_name="lbDbot",
                                email="lbdbot@lbdbot.com")

                # Get all meta data with the same description
                # they might be linked
                res = (sess.query(Meta)
                         .filter(Meta.description==meta.description,
                                 Meta.meta_column == None)
                         .all())

                # Create description tag to link them all
                # in once
                description = description_or_query(sess,
                                                   meta.meta_table,
                                                   meta.meta_type,
                                                   query)
                # Group by type and description
                key = (meta.meta_type, description,)

                if len(res) > 0:

                    obj = {"description":"%s: %s" % (meta.description, description),
                           "link": [r.meta_table.name for r in res ],
                           "user": user.json()}

                    if relations.get(key) is None:
                        relations[key] = obj
                    else:
                        relations.get(key)['link'] = list(set(relations.get(key)['link']) |
                                                          set(obj.get("link")))

                for r in res:
                    rels = (sess.query(RelationModel)
                            .filter(or_(RelationModel.tablel==r.meta_table,
                                        RelationModel.tabler==r.meta_table))
                            .distinct()
                            .all())

                    tabs = set()

                    for r in rels:
                        tabs |= set([r.tablel.name, r.tabler.name])

                    if len(tabs) > 0:
                        obj = {"description": "%s: %s" % (meta.description, description),
                               "link": list(tabs),
                               "user": user.json()}

                        if relations.get(key) is None:
                            relations[key] = obj
                        else:
                            relations.get(key)['link'] = list(set(relations.get(key)['link']) |
                                                              set(obj.get("link")))

                # Columns
                res = (sess.query(Meta).filter(Meta==meta, Meta.meta_table != None))
                column_list |= set([r.json() for r in res])

        docs.append({"tag": "tables", "res": table_list})
        docs.append({"tag": "relations", "res": relations.values()})
        docs.append({"tag": "columns", "res": list(column_list)})

    finally:
        sess.close()

    return docs


def description_or_query(sess, meta_table, meta_type, query):

    if meta_table is None:
        return query

    res = (sess.query(Meta)
               .filter(Meta.meta_table==meta_table,
                       Meta.meta_type=="other")
               .all())

    if len(res) > 0:
        desc = []

        for r in res:
            desc.append(r.description)
        return ', '.join(desc)

    return query


def run_parrallel(args):
    func, arguments = args
    return func(*arguments)


def filter_result(results, doc):
    if type(doc) == list:
        for d in doc:
            filter_result(results, d)
    else:
        obj = results[doc.get("tag")]
        for r in doc.get("res"):
            if r in obj:
                continue
            obj.append(r)


def query_search(query, directory):

    docs = {
        "tables": [],
        "columns": [],
        "relations": []
    }

    patterns = query.split()
    requests = []
    model = Modelize(directory=directory, draw_relations=True, relation_criterion="^REC")

    for pattern in patterns:
        args = (model, pattern,)
        requests.append((search_table, args,))
        requests.append((search_column, args,))
        requests.append((search_relation, args,))
        requests.append((search_meta, args,))

    p = Pool(4)

    results = p.map(run_parrallel, requests)
    p.close()
    p.join()

    for res in results:
        if res is None:
            continue
        filter_result(docs, res)

    return docs


if __name__ == '__main__':

    args = sys.argv[:1]

    try:
        print json.dumps(query_search(*args))
    except Exception as e:
        print e
