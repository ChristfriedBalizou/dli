import os
import shutil
import ConfigParser
import subprocess


CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
CFG_DIR = os.path.join(CURRENT_DIRECTORY, "graphviz.libd.cgf")

class AGraph(object):
    '''
    This class is an alternative to pygraphviz AGraph interface
    which directly invoke Graphviz ABI via subprocess.

    This class use a config file "graphviz.libd.cgf" to fetch
    Graphviz binary path and graph layour progam (e.i: dot, nano, ...)
    '''

    def __init__(self, doc):
        self.prog = 'dot'
        self.doc = doc
        self.path = None

        cfg = self.load_config('GRAPHVIZ', CFG_DIR)

        if not 'path' in cfg:
            raise Exception('Graphviz ABI path not specified in config file.')
        self.path = cfg.get('path')

        if 'layout' in cfg:
            self.prog = cfg.get('layout')


    def layout(self, prog='dot'):
        self.prog = prog


    def draw(self, filename):

        cmd = os.path.join(self.path, self.prog)

        with open(filename, 'w+b') as out:
            (subprocess.Popen([cmd, '-Tpng'],
                              stdout=out,
                              stdin=subprocess.PIPE)
                       .communicate(self.doc))

    @staticmethod
    def load_config(section, path):

        if path is None:
            raise IOError("Config file path 'None' not found")

        filepath = os.path.expanduser(path)

        if not os.path.exists(filepath):
            raise Exception("Config file %s not found." % path)
        config = ConfigParser.ConfigParser()
        config.read(filepath)
        return dict(config.items(section))


