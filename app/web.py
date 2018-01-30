'''
web.py
'''

from defs import func

from flask import Flask
from flask import Response
from flask import render_template
from flask import request
from flask import redirect, url_for
from flask import make_response

from tempfile import NamedTemporaryFile
from functools import wraps

import base64
import json
import os
import time
import logging
import struct

import argparse

logging.basicConfig(level=logging.INFO,
        format='%(asctime)-15s %(funcName)-8s %(levelname)-8s : %(message)s')

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DIRECTORY = os.path.join(CURRENT_DIRECTORY, '..', 'share')

APP = Flask(__name__)
APP.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
DELISTED = ("auth_login", "auth_logout")


def elapsed_time(func):

    def run(*args, **kwargs):
        now = time.time()
        result = func(*args, **kwargs)
        elapsed = "{}s".format(time.time() - now)
        logging.info(elapsed)
        return result + (elapsed,)

    return run


def extension(filename, ext):
    '''
    change file extension
    e.i: extension("test.ini", "png")
    >> test.png
    '''
    return "%s.%s" % (os.path.splitext(filename)[0], ext)


def wait_response(filename, counter=20, speed=0.5):

    counter = counter / speed
    i = 0

    while os.path.exists(filename) is False and i <= counter:
        if (i + 1) > counter:
            return False
        i = i + 1
        time.sleep(speed)

    return True


@elapsed_time
def run_request(obj):

    reqfile = None
    action = obj.get("action")

    if action != "tables":
        return func[action](APP.config.get("DATABASE_DIR"),
                            obj,
                            None,
                            None)

    with NamedTemporaryFile(mode='w+b',
                            dir=DIRECTORY,
                            prefix="libDWeb",
                            suffix=".req",
                            delete=False) as writer:
        reqfile = writer.name
        json.dump(obj, writer)

    resfile = extension(reqfile, 'res')

    logging.info("Sending request file %s" % os.path.basename(reqfile))
    return resfile, wait_response(resfile, speed=0.5)


def get_image_info(data):
    if is_png(data):
        w, h = struct.unpack('>LL', data[16:24])
        width = int(w)
        height = int(h)
    else:
        return 0, 0
    return width, height


def is_png(data):
    return (data[:8] == '\211PNG\r\n\032\n'and (data[12:16] == 'IHDR'))

def response_from_file(filename, status):
    docs = { "data" : None, "message" : None }
    short_filename = os.path.basename(filename)

    if status is True:
        logging.info("Response file %s recieved" % short_filename)
        with open(filename) as reader:
            res = json.load(reader)
            docs["data"] = res["response"]
            docs["message"] = res["message"]
        os.remove(filename)
    else:
        docs["message"] = "Timeout error processing request"
        logging.error("Timeout error processing request %s" %
                      extension(short_filename, 'req'))
    return docs


def process(req, authorization=None):

    docs = {"data" : None, "message": None}


    if not authorization and req.get("action") not in DELISTED:
        docs["message"] = "Login is required to access this ressource"
        return json.dumps({"response": docs, "status": False})

    if req.get("action") not in DELISTED:
        req.update({"auth": {
            "username": authorization.username,
            "password": authorization.password
            }})

    filename, status, elapsed = run_request(req)

    if req.get('action') != 'tables':
        docs["data"] = filename
        docs["message"] = status
        status = True
    else:
        docs = response_from_file(filename, status)

    if docs["message"] is not None:
        status = False

    if "auth" in req:
        del req["auth"]

    response = json.dumps({"query": req,
                           "response": docs,
                           "status": status,
                           "elapsed_time": elapsed}, indent=4)

    return response, 200


@APP.route("/")
def home(**kwargs):
    return render_template('index.html', **kwargs)


@APP.route("/login/", methods=["POST"])
def login():

    obj = request.get_json()

    req = {"action": "auth_login",
           "auth": {
               "username": obj.get("username"),
               "password": obj.get("password")
            }}

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/image/check/<name>", methods=["GET"])
def check_image(name):

    image_path = os.path.join(DIRECTORY, name)
    response = {"status": 0}

    if wait_response(image_path, speed=0.2) is True:
        response["status"] = 1

        with open(image_path) as img:
            w, h = get_image_info(img.read())
            response["size"] = {"w": w, "h": h}

    return Response(json.dumps(response),
                    status=200,
                    mimetype="application/json")


@APP.route("/image/<name>", methods=["GET"])
def get_image(name):

    bin_image = ""
    image_path = os.path.join(DIRECTORY, name)

    if wait_response(image_path, speed=0.2) is True:
        with open(image_path) as reader:
            bin_image = reader.read()

    os.remove(image_path)

    return Response(bin_image, status=200, mimetype="image/png")


@APP.route("/tables/<tables>/<columns>/<decoration>", methods=["GET"])
def tables_descriptions(tables, columns, decoration):

    columns = True if columns == "1" else False
    decoration = True if decoration == "1" else False

    req = {"action": "tables",
           "tables": tables.split(","),
           "show_columns": columns,
           "decoration": decoration}

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")

@APP.route("/statistics", defaults={"tables": ""}, methods=["GET"])
@APP.route("/statistics/<tables>", methods=["GET"])
def statistics(tables):

    req = {"action": "statistics",
           "tables": filter(bool, tables.split(","))}

    response, status = process(req, request.authorization)
    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/metadata/<category>/<name>/<meta_type>", methods=["GET", "POST"])
def metadata(category, name, meta_type):

    req = {"action": "metadata",
           "category": category,
           "meta_type": meta_type,
           "name": name}

    if request.method == "POST":
        req["action"] = "create_or_update_metadata"
        req.update(request.get_json())

    response, status = process(req, request.authorization)
    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/table/<name>", methods=["GET"])
def table(name):

    req = {"action": "table",
            "name": name }

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/tables", methods=["GET"])
def tables():

    req = {"action": "listTables"}

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/columns/<name>", methods=["GET"])
def columns(name):

    req = {"action": "columns",
           "name": name}

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/relation/<table_left>/<table_right>/", methods=["POST"])
def relation(table_left, table_right):

    req = {"action": "relation",
           "field": request.get_json(),
           "table_left": table_left,
           "table_right": table_right}

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")


def run(options):

    APP.config["DATABASE_DIR"] = os.path.expanduser(options.database)
    APP.run(port=options.port, host=options.server, processes=5)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--port',
                        default=5000,
                        help='Server port address')

    parser.add_argument('-s', '--server',
                        default='0.0.0.0',
                        help='Server IP address')

    parser.add_argument("-d", "--database",
                        required=True,
                        help="Database directory to introspec")

    if os.path.exists(DIRECTORY) is False:
        os.mkdir(DIRECTORY)

    run(parser.parse_args())



