'''
cli.py
'''

from defs import func

import argparse
import sys
import os
import json

CURRENT_DIRECTORY = os.path.dirname(os.path.relpath(__file__))
DIRECTORY = os.path.join(CURRENT_DIRECTORY, 'share')

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--database-directory',
                        default=None,
                        dest='directory',
                        help='Database directory')

    parser.add_argument('infile',
                        nargs='?',
                        type=argparse.FileType('r'),
                        default=sys.stdin)

    options = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if os.path.exists(DIRECTORY) is False:
        os.mkdir(DIRECTORY)

    req = json.loads(options.infile.read())

    response = None
    message = None
    action = req.get("action")

    try:
        if not action in func:
            message = "Requested action {} not found".format(action)
        else:
            response, message = func[action](options.directory, req, "cli.req", DIRECTORY)
    except Exception as e:
        message = str(e)

    print json.dumps({"response" : response, "message": message}, indent=4)
