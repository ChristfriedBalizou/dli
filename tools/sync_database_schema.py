'''
sync_database_schema.py

Help to download and update a database schema
'''

from auth.db import Database

import argparse
import sys
import os
import json
import shutil


CURRENT_DIRECTORY = os.path.dirname(os.path.relpath(__file__))
DB_SCHEMA_DIRECTORY = os.path.join(CURRENT_DIRECTORY, '..', 'DB_SCHEMA')
CONFIG_PATH = os.path.join(CURRENT_DIRECTORY, '..', "auth", "jeamsql.ini")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--directory',
                        default=DB_SCHEMA_DIRECTORY,
                        help='Database directory')

    parser.add_argument('--database',
                        default=None,
                        help='Database configuration name')

    parser.add_argument('--name',
                        default=None,
                        help='Database schema name')

    options = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    print "Downloading %s database schema" % options.database

    if os.path.exists(DB_SCHEMA_DIRECTORY) is False:
        os.mkdir(DB_SCHEMA_DIRECTORY)

    destination = os.path.join(DB_SCHEMA_DIRECTORY, options.name)
    new_destination = "%s.NEW" % destination
    database = Database(section=options.database, config_path=CONFIG_PATH)

    if os.path.exists(new_destination):
        os.rmdir(new_destination)

    os.mkdir(new_destination)

    docs = json.loads(database.tables(fmt="json"))

    print "%s tables found" % len(docs)

    for tab in docs:
        cols = json.loads(database.description(table_name=tab['table_name'],
                                               fmt="json"))

        print "%s columns found for table %s" % (len(cols), tab["table_name"])

        with open(os.path.join(new_destination, tab['table_name']), 'w') \
                as table_write:
            table_write.write('\n'.join([col['column_name'] for col in cols]))


    if os.path.exists(destination):
        os.rmdir(destination)

    shutil.move(new_destination, destination)
