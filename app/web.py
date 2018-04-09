'''
web.py
'''

from app.defs import func
from auth.auth import Auth

from flask import Flask, session
from flask import Response
from flask import render_template
from flask import request

from flask_session import Session

from tempfile import NamedTemporaryFile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import json
import os
import time
import logging
import struct
import copy
import uuid
import smtplib

import argparse

logging.basicConfig(level=logging.INFO,
        format='%(asctime)-15s %(funcName)-8s %(levelname)-8s : %(message)s')

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DIRECTORY = os.path.join(CURRENT_DIRECTORY, '..', 'share')

APP = Flask(__name__)
APP.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
DELISTED = ("auth_login", "auth_logout", "databases")
authenticator = Auth.Instance()


def send_mail(token, email, sender="noreply-lbdi@amundi.com"):

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "[lbDi Tool] Library DECALOG interface password reset link"
    msg['From'] = sender
    msg['to'] = email

    link = "http://tst-clappdecalog:5555/#reset-password/%s" % token

    html ="""\
            <html>
                <head></head>
                <body>
                    Copy and paste the following link in your <b>Google Chrome</b> or <b>Firefox</b> <br/>
                    to reset you lbDi password<br>
                    <a href="%s">%s</a> <br/><br/>

                    Regards,<br/>
                    lbDi - Library DECALOG interface
                </body>
            </html>
    """ % (link, link)

    msg.attach(MIMEText(html, 'html'))

    email_server = APP.config.get("email_server")

    if email_server is None:
        email_server = 'localhost'

    s = smtplib.SMTP(email_server)
    s.sendmail(sender, email, msg.as_string())
    s.quit()


def elapsed_time(func):

    def run(*args, **kwargs):
        now = time.time()
        result = func(*args, **kwargs)
        elapsed = "{}s".format(time.time() - now)
        return result + (elapsed,)

    return run


def requires_auth(username, password):

        ok, _ = authenticator.check_authentication(username, password)

        if ok is False:
            return ok, "Wrong username or password"

        return ok, None


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

    action = obj.get("action")

    response, message = func[action](APP.config.get("DATABASE_DIR"),
                                     obj,
                                     None,
                                     None)

    if action != "tables":
        return response, message

    # If it's tables request ask to pre-draw graph
    with NamedTemporaryFile(mode='w+b',
                            dir=DIRECTORY,
                            prefix="libDWeb",
                            suffix=".req",
                            delete=False) as writer:
        doc_req = copy.deepcopy(obj)
        doc_req["action"] = "draw_dot"

        doc_req.update(response)
        json.dump(doc_req, writer)
        response["filename"] = extension(os.path.basename(writer.name), "png")

    return response, message


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
    ok = True


    if not authorization and req.get("action") not in DELISTED:
        docs["message"] = "Login is required to access this ressource"
        return json.dumps({"response": docs, "status": False})

    if req.get("action") not in DELISTED:
        req.update({"auth": {
            "username": authorization.username,
            "password": authorization.password
            }})

        # try to authenticate user
        ok, msg = requires_auth(authorization.username, authorization.password)

    if ok is True:
        data, msg, elapsed = run_request(req)

    docs["data"] = data
    docs["message"] = msg
    status = True

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

    req = {"action": "databases"}
    response, _=  process(req)
    return render_template('index.html',
                           databases=json.loads(response),
                           **kwargs)


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


@APP.route("/<database>/tables/<tables>/", methods=["POST"])
def tables_descriptions(database, tables):

    req = {"action": "tables",
           "tables": tables.split(","),
           "decoration": False,
           "show_columns": False,
           "draw_ai": True,
           "draw_human": True,
           "draw_deleted": True,
           "db_name": database}

    req.update(request.get_json())

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")

@APP.route("/<database>/statistics", defaults={"tables": ""}, methods=["GET"])
@APP.route("/<database>/statistics/<tables>", methods=["GET"])
def statistics(database, tables):

    req = {"action": "statistics",
           "tables": filter(bool, tables.split(",")),
           "db_name": database}

    response, status = process(req, request.authorization)
    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/<database>/metadata/<category>/<name>/<meta_type>", methods=["GET", "POST"])
def metadata(database, category, name, meta_type):

    req = {"action": "metadata",
           "category": category,
           "meta_type": meta_type,
           "name": name,
           "db_name": database}

    if request.method == "POST":
        req["action"] = "create_or_update_metadata"
        req.update(request.get_json())

    response, status = process(req, request.authorization)
    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/<database>/table/<name>", methods=["GET"])
def table(database, name):

    req = {"action": "table",
            "name": name,
            "db_name": database}

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/<database>/search/", methods=["POST"])
def text_search(database):

    query = request.get_json()

    req = {"action": "search",
           "query": query.get("query"),
           "db_name": database}

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/<database>/tables", methods=["GET"])
def tables(database):

    req = {"action": "listTables", "db_name": database}

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/<database>/columns/<name>", methods=["GET"])
def columns(database, name):

    req = {"action": "columns",
           "name": name,
           "db_name": database}

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/<database>/tables/column/<name>", methods=["GET"])
def get_tables_by_column(database, name):

    req = {"action": "tables_by_column",
            "name": name,
            "db_name": database}

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/<database>/relation/<table_left>/<table_right>/", methods=["POST"])
def relation(database, table_left, table_right):

    req = {"action": "relation",
           "field": request.get_json(),
           "table_left": table_left,
           "table_right": table_right,
           "db_name": database}

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")


@APP.route("/forgot_password/<email>", methods=["GET"])
def forgot_password(email):

    response = {"status": True}

    user = authenticator.get_user_by_email(email)

    if user is None:
        response["status"] = False
    else:
        token = uuid.uuid4().hex
        session[token] = user
        send_mail(token, email)

    return Response(json.dumps(response, indent=4),
                    status=200,
                    mimetype="application/json")


@APP.route("/reset_password/<email>/", methods=["POST"])
def reset_password(email):

    response = {"status": True}

    obj = request.get_json()

    status = authenticator.update_password(email, obj.get("newPassword"))

    response["status"] = status

    return Response(json.dumps(response, indent=4),
                    status=200,
                    mimetype="application/json")


@APP.route("/user/<token>", methods=["GET"])
def get_user_by_token(token):

    response = {"data": None, "status": True}

    response["data"] = session.get(token)

    if session.get(token) is not None:
        del session[token]

    if response["data"] is None:
        response["status"] = False

    return Response(json.dumps(response, indent=4),
                    status=200,
                    mimetype="application/json")


@APP.route("/fam", methods=["GET"])
def wall_of_fam():

    req = {"action": "wall_of_fam"}

    response, status = process(req, request.authorization)

    return Response(response,
                    status=status,
                    mimetype="application/json")

def run(options):

    APP.config["DATABASE_DIR"] = os.path.expanduser(options.database)
    APP.config["email_server"] = options.email_server
    APP.secret_key = 'd35feb998e3647a4a665284078bd5c38'
    APP.config['SESSION_TYPE'] = 'filesystem'

    sess = Session()
    sess.init_app(APP)

    APP.run(port=options.port, host=options.server, processes=5)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--port',
                        default=5000,
                        help='Server port address')

    parser.add_argument('-s', '--server',
                        default='0.0.0.0',
                        help='Server IP address')

    parser.add_argument('--server-email',
                        default=None,
                        dest="email_server",
                        help='Host email server')

    parser.add_argument("-d", "--database",
                        required=True,
                        help="Database directory to introspec")

    if os.path.exists(DIRECTORY) is False:
        os.mkdir(DIRECTORY)

    run(parser.parse_args())



