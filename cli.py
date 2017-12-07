from tools.modelize import Modelize
from tools.template import Dotit

import pygraphviz as graph

import argparse
import sys
import json
import os


def modelize(*args, **kwargs):
    return Modelize(**kwargs)


def draw(*args, **kwargs):

    dot = Dotit(**kwargs)

    libdG = graph.AGraph(dot.render())
    libdG.layout(prog=options.layout)

    output = os.path.expanduser(options.output)
    directory = os.path.dirname(output)

    if directory == '':
        directory = './'

    if not os.path.exists(directory):
        os.makedirs(directory)

    libdG.draw(output)

    return output


def run(options):

    model = modelize(
            directory=options.directory,
            table_list=options.table_list,
            draw_relations=options.relations,
            relation_criterion=options.pattern)


    if options.print_tables:
        return model.tables()

    return draw(docs=model.dot(), relations=model.dot_relations())


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--output',
            default='diagram.png',
            help='Output file path'
            )

    parser.add_argument('-r', '--relations',
            default=False,
            action='store_true',
            help='Draw relations on graph if mentioned')

    parser.add_argument('--print-tables',
            default=False,
            action='store_true',
            help='Print all tables in database scheme')

    parser.add_argument('-t', '--table-list',
            default=[],
            nargs='*',
            dest='table_list',
            help='Table list to match'
            )

    parser.add_argument('-i', '--input-directory',
            default=None,
            dest='directory',
            help='Tables scheme directory'
            )

    parser.add_argument('-p', '--pattern',
            default='^REC',
            help="Do not create relation with the follogin match",
            )

    parser.add_argument('-l', '--layout',
            default='dot',
            help="Program used by Graphiz to draw the graph",
            )

    options = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)


    print run(options)
