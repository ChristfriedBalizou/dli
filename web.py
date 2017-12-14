from flask import Flask

import argparse

app = Flask(__name__)

def run(options):

    app.run(port=options.port, host=options.server)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--port',
            default=5000,
            help='Server port address'
            )

    parser.add_argument('-s', '--server',
            default='0.0.0.0',
            help='Server IP address')

    run(parser.parse_args())



