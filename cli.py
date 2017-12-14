'''
cli.py
'''

from tools.modelize import Modelize
from tools.template import Dotit

import pygraphviz as graph

import argparse
import sys
import os


def modelize(**kwargs):
    '''
    modelize introspect and extract data in json format
    '''
    return Modelize(**kwargs)


def draw(filename, docs=[], relations=[], layout='dot'):
    '''
    Use pygraph to draw class diagram
    '''

    dot = Dotit(docs=docs, relations=relations)

    libdG = graph.AGraph(dot.render())
    libdG.layout(prog=layout)

    output = os.path.expanduser(filename)
    directory = os.path.dirname(output)

    if directory == '':
        directory = './'

    if not os.path.exists(directory):
        os.makedirs(directory)

    libdG.draw(output)

    return output


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--output',
                        default='diagram.png',
                        help='Output file path')

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
                        help='Table list to match')

    parser.add_argument('-i', '--input-directory',
                        default=None,
                        dest='directory',
                        help='Tables scheme directory')

    parser.add_argument('-p', '--pattern',
                        default='^REC',
                        help="Do not create relation with the follogin match")

    parser.add_argument('-l', '--layout',
                        default='dot',
                        help="Program used by Graphiz to draw the graph")

    options = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    model = modelize(table_list=options.table_list,
                     draw_relations=options.relations,
                     relation_criterion=options.pattern)

    if options.print_tables:
        print model.tables()

    print  draw(docs=model.dot(),
                relations=model.dot_relations(),
                filename=options.directory,
                layout=options.layout)
