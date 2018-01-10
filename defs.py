from cli import modelize, draw
from models import (
        TableModel,
        ColumnModel,
        RelationModel,
        User,
        Meta,
        DBsession
        )

from auth.auth import Auth
from datetime import datetime
from sqlalchemy import or_
from collections import defaultdict
import logging
import os
import json

auth_context = Auth.Instance()

def extension(filename, ext):
    '''
    change file extension
    e.i: extension("test.ini", "png")
    >> test.png
    '''
    return "%s.%s" % (os.path.splitext(filename)[0], ext)


def list_table(database, req, filename, directory):
    response = None
    message = None
    try:
        model = modelize(directory=database)
        response = model.list_table()
    except Exception as e:
        message = str(e)
        logging.error(e)

    return response, message


def compute_relations(computed_relation, remove_deleted=False):

    sess = DBsession()

    # load relations from database
    db_rels = []
    docs = defaultdict(list)
    deleted_rel = []

    for rel in computed_relation:
        tablel = get_or_create(sess, TableModel, name=rel.get("a"))
        tabler = get_or_create(sess, TableModel, name=rel.get("b"))

        rels = (sess.query(RelationModel)
                .filter_by(tablel=tablel,
                           tabler=tabler)
                .all())
        db_rels.extend(rels)

    for db_rel in db_rels:
        rela = {"left": db_rel.columnl.name,
                "right": db_rel.columnr.name,
                "is_deleted": db_rel.is_deleted,
                "relation_type": "human"}

        if db_rel.is_deleted is True and remove_deleted is True:
            deleted_rel.append((db_rel.tablel.name, db_rel.tabler.name,))
            continue

        docs[(db_rel.tablel.name, db_rel.tabler.name,)].append(rela)

    res = []

    for rel in computed_relation:
        key = (rel.get("a"), rel.get("b"),)

        if remove_deleted is True and key in deleted_rel:
            continue

        if key in docs:
            docs[key] = remove_equal_relations(docs[key], rel.get("fields"))
        else:
            docs[key] = rel.get("fields")

    for key, value in docs.items():
        left_table, right_table = key
        res.append({"a": left_table,
                    "b": right_table,
                    "fields": value})

    return res


def remove_equal_relations(to_keep, add_maybe):

    results = defaultdict(list)

    for field in to_keep:
        key = (field.get("left"), field.get("right"),)
        results[key].append(field)

    for field in add_maybe:
        key = (field.get("left"), field.get("right"),)
        if key in results:
            continue
        results[key].append(field)

    out = []
    for _, value in results.items():
        out.extend(value)
    return out


def tables_descriptions(database, req, filename, directory):
    response = None
    message = None

    try:
        model = modelize(directory=database,
                         relation_criterion="^REC",
                         draw_relations=True,
                         table_list=req.get("tables"))

        new_filename = extension(filename, 'png')
        file_path = os.path.join(directory, new_filename)

        docs = model.dot()
        relations = compute_relations(model.dot_relations())
        draw(file_path,
             'dot',
             docs=docs,
             relations=relations,
             decoration=req.get("decoration"),
             show_columns=req.get("show_columns"),
             hdel_color="#BDBDBD",
             h_color="#009688",
             ai_color="#2196F3",
             color="white",
             text_color="#222222",
             bgcolor="#EEEEEE",
             table_bgcolor="#3F51B5")

        response = {"filename": extension(filename, 'png'),
                    "relations": list(relations)}
    except Exception as e:
        message = str(e)
        logging.error(e)

    return response, message


def statistics(database, req, filename, directory):

    response = None
    message = None

    try:
        model = modelize(directory=database,
                         relation_criterion="^REC",
                         draw_relations=True,
                         table_list=req.get("tables"))
        response = model.statistics()
    except Exception as e:
        message = str(e)
        logging.error(e)

    return response, message


def relation(database, req, filename, directory, **kwargs):

    response = None
    message = None

    username = req.get("auth").get("username")

    try:
        sess = DBsession()

        # get user doing action
        user = sess.query(User).filter_by(username=username).first()

        # look for left table
        tablel = get_or_create(sess,
                               TableModel,
                               name=req.get("table_left"))
        # look for right table
        tabler = get_or_create(sess,
                               TableModel,
                               name=req.get("table_right"))

        field = req.get("field")
        left_col = get_or_create(sess,
                                 ColumnModel,
                                 name=field.get("left"))

        right_col = get_or_create(sess,
                                  ColumnModel,
                                  name=field.get("right"))

        rel = get_or_create(sess,
                            RelationModel,
                            tablel=tablel,
                            tabler=tabler,
                            columnl=left_col,
                            columnr=right_col)

        rel.is_deleted=field.get("is_deleted")
        rel.user = user

        sess.commit()
        sess.close()
        response = json.dumps(req, indent=4)
    except Exception as e:
        message = str(e)
        logging.error(e)

    return response, message

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def get_table_columns(database, req, filename, directory, **kwargs):

    message = None
    response = None

    try:
        model = modelize(directory=database)
        columns = model.table_skeleton(name=req.get("name"))

        if columns is None:
            message = "Table %s not found" % req.get("name")

        response = sorted(columns.get(req.get("name")))

    except Exception as e:
        message = str(e)
        logging.error(e)

    return response, message


def login(database,
               req,
               filename,
               directory,
               authenticator=auth_context):

    response = None
    message = None

    if not "auth" in req:
        message = "Bad authentication request"

    username = req.get("auth").get("username")
    password = req.get("auth").get("password")

    ok, user = authenticator.check_authentication(username, password)

    if ok is True:
        response = user.json()
    else:
        message = "Wrong username or password"

    return response, message


def logout(database,
           req,
           filename,
           directory,
           authenticator=auth_context):

    response = None
    message = None

    if not "auth" in req:
        message = "Bad authentication request"

    username = req.get("auth").get("username")
    authenticator.logout(username)

    return response, message


def describ_table(database,
                  req,
                  filename,
                  directory,
                  **kwargs):

    response = None
    message = None

    try:
        sess = DBsession()

        meta_table = get_or_create(sess, TableModel, name=req.get("name"))
        meta_data = (sess.query(Meta)
                         .filter_by(meta_table=meta_table)
                         .all())

        description = {}
        tags = []
        other = []
        related = []
        added_to_related = []

        for m in meta_data:
            if m.meta_type == "description":
                description = m.json()
            if m.meta_type == "tag":
                tags.append(m.json())
            if m.meta_type == "other":
                other.append(m.json())
            if m.meta_type == "related":
                related.append(m.json())
                added_to_related.append(m.description)

        # get possible related from database and automaticaly
        rels = (sess.query(RelationModel)
                    .filter(or_(RelationModel.tablel==meta_table,
                                   RelationModel.tabler==meta_table),
                               RelationModel.is_deleted==False)
                    .all())

        for r in rels:
            if r.tablel.name in added_to_related:
                continue
            if r.tabler.name in added_to_related:
                continue

            table_name = None
            if r.tablel.name == meta_table.name:
                table_name = r.tabler.name
            else:
                table_name = r.tablel.name

            related.append({"description": table_name,
                "type": "related",
                "user": None,
                "table": meta_table.name,
                "column_name": None,
                "record_date": datetime.now().strftime('%Y-%m-%d')
                })
            added_to_related.append(table_name)

        response = {"description": description,
                    "tags": tags,
                    "other": other,
                    "related": related}
    except Exception as e:
        message = str(e)
        logging.error(e)

    return response, message



# All exposed function should be placed here
func = {"listTables": list_table,
        "statistics": statistics,
        "tables": tables_descriptions,
        "relation": relation,
        "columns": get_table_columns,
        "auth_login": login,
        "auth_logout": logout,
        "table": describ_table}
