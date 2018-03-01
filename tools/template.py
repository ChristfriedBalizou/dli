'''
This file containt dot template to generate a correct dot file.
Note the default color scheme and style was inspired from:
dango-extensions graph_models which look more pleasant and clear

https://github.com/django-extensions/django-extensions

'''
from collections import defaultdict


class Dotit(object):

    def __init__(self,
            fontname='Helvetica',
            fontsize=8,
            splines=True,
            style="rounded",
            color="olivedrab4",
            text_color="#7B7B7B",
            bgcolor="palegoldenrod",
            table_bgcolor="olivedrab4",
            h_color="#000000",
            hdel_color="#000000",
            ai_color="#000000",
            shape="plaintext",
            decoration=True,
            docs=None,
            show_columns=True,
            draw_human=True,
            draw_ai=True,
            draw_deleted=True,
            relations=None):

        # Formating
        self.fontname = fontname
        self.fontsize = fontsize
        self.splines = splines
        self.shape = shape
        self.color = color
        self.text_color = text_color
        self.bgcolor = bgcolor
        self.h_color = h_color
        self.hdel_color = hdel_color
        self.ai_color = ai_color
        self.table_bgcolor = table_bgcolor
        self.style = style
        self.decoration = decoration

        #Data
        self.docs = docs
        self.relations = relations

        # Options
        self.show_columns = show_columns
        self.draw_human = draw_human
        self.draw_ai = draw_ai
        self.draw_deleted = draw_deleted



    def render(self, docs=None, relations=None):

        if docs is not None:
            self.docs = docs

        if relations is not None:
            self.relations = relations

        splines = "true"

        if self.splines is False:
            splines = "false"

        result = '''
        digraph model_graph {

            fontname = "%s"
            fontsize = %s
            splines  = %s

            %s

            %s

        ''' % (self.fontname, self.fontname, splines, self.node(), self.edge())


        for sub in self.docs:

            tables = []

            for tab in sub.get("tables"):

                rows = []

                if self.show_columns is True:
                    rows = [self.rows(f) for f in tab.get("fields")]

                name = tab.get("name").replace('#', "TEMP").replace('.', '_')

                entity = self.entity(
                        name,
                        '\n'.join(rows)
                        )

                tables.append(entity)

            doc = self.subgraph(
                    sub.get("name"),
                    self.graph_label(sub.get("name")),
                    '\n'.join(tables))

            result = '''
                %s

                %s
            ''' % (result, doc)

        for relation in self.relations:
            result = '''
                %s

                %s
            ''' % (result, self.relation(relation.get("a"),
                                         relation.get("b"),
                                         fields=relation.get("fields")))

        result = '''
            %s
        }
        ''' % (result)

        return result



    def node(self):
        return '''
            node [
                fontname = "%s"
                fontsize = %s
                shape = "%s"
            ]
        ''' % (self.fontname, self.fontsize, self.shape)


    def edge(self, color="#000000"):
        return '''
            edge [
                fontname = "%s"
                fontsize = %s
                color = "%s"
                fontcolor = "%s"
            ]
        ''' % (self.fontname, self.fontsize, color, color)


    def subgraph(self, name, graph_label, content):

        if self.decoration is not True:
            graph_label = ""

        return '''
            subgraph cluster_%s {
                label=<
                      %s
                      >
                color=%s
                style=%s
                %s
            }
        ''' % (name, graph_label, self.color, self.style, content)


    def graph_label(self, name):

        return '''
              <TABLE BORDER="0" CELLBORDER="0">
              <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER">
              <FONT FACE="%s Bold" COLOR="Black" POINT-SIZE="12">
              %s
              </FONT>
              </TD></TR>
              </TABLE>
        ''' % (self.fontname, name)


    def entity(self, name, rows=""):
        return '''
            %s [label=<
              <TABLE BGCOLOR="%s" BORDER="0" CELLBORDER="0" CELLSPACING="0">
              <TR><TD COLSPAN="2" CELLPADDING="4" ALIGN="CENTER" BGCOLOR="%s">
              <FONT FACE="%s Bold" COLOR="white">
                %s
              </FONT>
              </TD></TR>

                %s

                </TABLE>
            >]
        ''' % (name, self.bgcolor, self.table_bgcolor, self.fontname, name, rows)


    def rows(self, col):
        return '''
              <TR>
                  <TD ALIGN="LEFT" BORDER="0">
                  <FONT COLOR="%s" FACE="Helvetica ">%s</FONT>
                  </TD>
                  <TD ALIGN="LEFT" BORDER="0">
                  </TD>
              </TR>
        ''' % (self.text_color, col)


    def relation(self, a, b, fields=[]):

        docs=""

        by_relation_type = defaultdict(list)

        for f in fields:
            key = f.get("relation_type")

            if f.get("is_deleted") is True:
                key = "deleted"

            by_relation_type[key].append(f)


        for rel, fields in by_relation_type.items():

            color = "#000000"
            style = "filled"

            if rel == "human":
                color = self.h_color

            if rel == "ai":
                color = self.ai_color

            if rel == "deleted":
                color = self.hdel_color
                style = "dotted"

            if self.draw_human is False and rel == "human":
                continue
            if self.draw_ai is False and (rel == "ai" or rel is None):
                continue
            if self.draw_deleted is False and rel == "deleted":
                continue

            docs = '''
                %s
                %s -> %s [color="%s", fontcolor="%s", style=%s]
                [label="%s"] [arrowhead=none, arrowtail=none, dir=both]
            ''' % (docs, a, b, color, color, style, self.fields_to_label(fields))

        return docs


    def fields_to_label(self, fields):

        result = ""

        for f in fields:

            right = f.get("right")
            left = f.get("left")

            if right == left:
                result = "%s, %s" % (result, left)
            else:
                result = "%s, %s - %s" % (result, left, right)

        return result[2:]
