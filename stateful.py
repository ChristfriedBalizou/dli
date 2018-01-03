'''
 A statefull version of libD
'''
from defs import func
from auth.auth import Auth

from multiprocessing import Pool
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

import sys
import logging
import argparse
import os
import json
import time
import shutil

DIRECTORY = os.path.join('./', 'share')
DATABASE_DIR = ""
authenticator = Auth()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def requires_auth(req, auth_context):

        if not "auth" in req:
            return False, "Login is required to access this function"

        username = req.get("auth").get("username")
        password = req.get("auth").get("password")

        ok, _ = auth_context.check_authentication(username, password)

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


def run_parrallel(args):
    '''
    Execute the given request in a different thread
    '''
    req, filename, directory = args

    logging.info("execute request: {}".format(filename))

    response = None
    message = None
    action = req.get("action")

    ok, msg = requires_auth(req, authenticator)

    if ok is False and not action.startswith("auth_"):
        message = msg
    elif not action in func:
        message = "Requested action {} not found".format(action)
    else:
       response, message = func[action](DATABASE_DIR, *args)

    file_path = os.path.join(directory, extension(filename, 'res'))

    with open(file_path, "wb") as writer:
        json.dump({"response" : response, "message": message}, writer)

    os.remove(os.path.join(directory, filename))
    logging.info("Done")


def run(filename, directory):

    '''
    Process files request
    '''

    if os.path.splitext(filename)[1] != '.req':
        return

    requests = []
    logging.info("Processing request file " + filename)

    try:
        with open(os.path.join(directory, filename)) as reader:
            requests.append((json.load(reader), filename, directory,))
    except Exception as e:
        print e

    p = Pool(2)
    p.map(run_parrallel, requests)

    p.close()
    p.join()


class Stateful(LoggingEventHandler):

    '''
    Stateful
    '''

    def process(self, event, path=None):

        '''
        dispatcher
        '''
        src_path = event.src_path

        if path is not None:
            src_path = path

        filename = os.path.basename(src_path)
        directory = os.path.dirname(src_path)
        run(filename, directory)


    def on_created(self, event):
        self.process(event)


    def on_moved(self, event):

        if event.is_directory:
            return

        self.process(event, path=event.dest_path)


    def on_modified(self, event):
        self.process(event)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--directory",
                        default="./share",
                        help="Exchange directory")

    parser.add_argument("--database",
                        required=True,
                        help="Database directory to introspec")

    options = parser.parse_args()

    DIRECTORY = os.path.expanduser(options.directory)
    DATABASE_DIR = os.path.expanduser(options.database)

    if DATABASE_DIR is None or not os.path.exists(DATABASE_DIR):
        logging.error("Missing database directory")
        sys.exit(1)

    if not os.path.exists(DIRECTORY):
        os.mkdir(DIRECTORY)

    event_handler = Stateful()

    observer = Observer()
    observer.schedule(event_handler, DIRECTORY, recursive=True)
    observer.start()

    try:
        logging.info("Watching directory {} for changes".format(DIRECTORY))
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
