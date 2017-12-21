'''
 A statefull version of libD
'''

from cli import modelize, draw

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

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


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

    if req.get("action") == "listTables":

        try:
            model = modelize(directory=DATABASE_DIR)
            response = model.list_table()
        except Exception as e:
            message = str(e)
            logging.error(e)

    elif req.get("action") == "tables":

        try:
            model = modelize(directory=DATABASE_DIR,
                             relation_criterion="^REC",
                             draw_relations=True,
                             table_list=req.get("tables"))

            new_filename = extension(filename, 'png')
            file_path = os.path.join(directory, new_filename)

            docs = model.dot()
            relations = model.dot_relations()
            draw(file_path,
                 docs=docs,
                 relations=relations)

            response = [extension(filename, 'png')]
        except Exception as e:
            message = str(e)
            logging.error(e)

    elif req.get("action") == "statistics":

        try:
            model = modelize(directory=DATABASE_DIR,
                             relation_criterion="^REC",
                             draw_relations=True,
                             table_list=req.get("tables"))
            response = model.statistics()
        except Exception as e:
            message = str(e)
            logging.error(e)

    elif req.get("action") is None:
        message = "No action to execute found"
    else:
        message = "Requested action {} not found".format(req.get("action"))

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
