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
import subprocess


CURRENT_DIRECTORY = os.path.dirname(os.path.relpath(__file__))
DIRECTORY = os.path.join(CURRENT_DIRECTORY, '..', 'share')
DATABASE_DIR = ""
AUTHENTICATION_EXCEMPT = ('auth_login',
                          'auth_logout',
                          'draw_dot',)
authenticator = Auth.Instance()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

if os.path.exists(DIRECTORY) is False:
    os.mkdir(DIRECTORY)


def rsync(src, dest, args=""):

    '''
    Copy file from destination to remote
    '''

    cmd = 'rsync -avzP {} {} {}'.format(
            args,
            src,
            dest
        )

    with open(os.devnull, 'w') as DEVNULL:
        subprocess.call(
                cmd.split(' '),
                stdout=DEVNULL,
                stderr=subprocess.STDOUT)


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

    try:
        if ok is False and action not in AUTHENTICATION_EXCEMPT:
            message = msg
        elif not action in func:
            message = "Requested action {} not found".format(action)
        else:
           response, message = func[action](DATABASE_DIR, *args)
    except Exception as e:
        message = str(e)
        logging.error(e)

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

    p = Pool(5)
    p.map(run_parrallel, requests)

    p.close()
    p.join()


class Stateful(LoggingEventHandler):

    '''
    Stateful
    '''


    def __init__(self, destination, sync_remote=False):

        super(Stateful, self).__init__()
        self.sync_remote = sync_remote
        self.destination = destination


    def process(self, event, path=None):

        '''
        dispatcher
        '''
        src_path = event.src_path

        if path is not None:
            src_path = path

        filename = os.path.basename(src_path)
        directory = os.path.dirname(src_path)

        if filename.endswith(".req"):
            run(filename, directory)

        if filename.endswith(".png") and self.sync_remote is not None:
            rsync(src_path, self.destination, args="--remove-source-files")


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

    parser.add_argument("-s", "--source",
                        default=DIRECTORY,
                        help="Source directory")

    parser.add_argument("-d", "--destination",
                        required=True,
                        help="Destination directory")

    parser.add_argument("-p", "--pull-request",
                        dest="pull_request",
                        default=False,
                        action="store_true",
                        help="Pull request from destination directory")

    parser.add_argument("--database",
                        required=True,
                        help="Database directory to introspec")

    options = parser.parse_args()

    if options.destination is None:
        parser.print_help()
        sys.exit(1)

    DIRECTORY = os.path.expanduser(options.source)
    DATABASE_DIR = os.path.expanduser(options.database)

    if DATABASE_DIR is None or not os.path.exists(DATABASE_DIR):
        parser.print_help()
        sys.exit(1)

    if not os.path.exists(DIRECTORY):
        os.mkdir(DIRECTORY)

    event_handler = Stateful(options.destination,
                             sync_remote=options.pull_request)

    observer = Observer()
    observer.schedule(event_handler, DIRECTORY, recursive=True)
    observer.start()

    try:
        logging.info("Watching directory {} for changes".format(DIRECTORY))

        while True:

            if options.pull_request is True:
                rsync("%s/*.req" % options.destination,
                      options.source,
                      args="--remove-source-files")

            time.sleep(0.5)

    except KeyboardInterrupt:
        observer.stop()
    observer.join()
