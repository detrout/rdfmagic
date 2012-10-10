import os
import re
import sys
import urllib
if sys.version_info.major == 3:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

import RDF
import collections

from IPython.core import page
from IPython.core.magic import (Magics, magics_class, cell_magic, line_magic,
                                line_cell_magic, needs_local_scope, UsageError)
from IPython.core.magic_arguments import (
    argument, magic_arguments, parse_argstring)

from IPython.core.displaypub import (
    publish_pretty, publish_html,
    publish_latex, publish_svg,
    publish_png, publish_json,
    publish_javascript, publish_jpeg
)

from IPython.core.display import HTML

_prefixes = {
    'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    'rdfs': "http://www.w3.org/2000/01/rdf-schema#",
    'owl': 'http://www.w3.org/2002/07/owl#',
    'dc': "http://purl.org/dc/elements/1.1/",
    'xml': 'http://www.w3.org/XML/1998/namespace',
    'xsd': "http://www.w3.org/2001/XMLSchema#",
    'vs': 'http://www.w3.org/2003/06/sw-vocab-status/ns#',
    'wot': 'http://xmlns.com/wot/0.1/'
}
_namespaces = dict(( (v, k) for k, v in _prefixes.items()))

def dump_model(model):
    export = RDF.Serializer(name='turtle')
    print (export.serialize_model_to_string(model))
    
def display_node(node, mime_type):
    if mime_type == 'text/html':
        template = '<a href="{anchor}">{curie}</a>'
    else:
        template = '{curie}'
    
    if isinstance(node, RDF.Node) and node.is_resource():
        match = ""
        uri = str(node.uri)
        curie = uri
        for namespace, prefix in _namespaces.items():
            if uri.startswith(namespace) and len(namespace) > len(match):
                match = namespace

        if len(match) > 0:
            prefix = _namespaces[match]
            curie = uri.replace(match, "{0}:".format(prefix))

        return template.format(anchor=uri, curie=curie)
    else:
        return str(node)


class Node(RDF.Node):
    def _repr_html_(self):
        return display_node(self, mime_type='text/html')

Uri = RDF.Uri
NS = RDF.NS

class LibRdfResults(collections.Sequence):
    results = None
    columns = None
    def __init__(self, result_set):
        if result_set is not None:
            self.columns = self.get_bindings(result_set)
            self.results = self.get_results(result_set)

    def get_bindings(self, result_set):
        b = []
        for i in xrange(result_set.get_bindings_count()):
            b.append(result_set.get_binding_name(i))
        return b

    def get_results(self, result_set):
        results = []
        for row in result_set:
            record = [ row[k] for k in self.columns ]
            results.append(record)
        return results

    def __getitem__(self, key):
        return dict(zip(self.columns, self.results[key]))

    def __len__(self):
        return len(self.results)

    def generate_html(self):
        result_set = iter(self)
        yield '<table><tr>'
        for c in self.columns:
            yield "<td>{0}</td>".format(str(c))
        yield '</tr>'
        for row in self:
            yield '<tr>'
            for key in self.columns:
                value = row[key]
                yield '<td>'
                yield display_node(value, mime_type='text/html')
                yield '</td>'
            yield '</tr>'
        yield '</table>'

    def _repr_html_(self):
        return "".join(self.generate_html())

    def __str__(self):
        result_set = iter(self)
        output = []
        output.append("\t".join(self.columns))
        for row in self.results:
            ordered = (display_node(value, mime_type='text/plain')
                       for value in row)
            output.append("\t".join(ordered))
        return os.linesep.join(output)

@magics_class
class SPARQLMagics(Magics):
    SUPPORT_FROM = False
    def __init__(self, shell):
        super(SPARQLMagics, self).__init__(shell)

    @magic_arguments()
    @argument('prefix', nargs=1, type=str,
              help="Specify namespace prefix")
    @argument('namespace', nargs=1, type=str,
              help="specify namespace")
    @line_magic
    def addns(self, line):
        args = parse_argstring(self.addns, line)
        if args.prefix is None or args.namespace is None:
            raise UsageError("Please specify prefix and namespace")
        namespace = args.namespace[0]
        prefix = args.prefix[0]
        _namespaces[namespace] = prefix
        _prefixes[prefix] = namespace

    @line_magic
    def lsns(self, line=None):
        keys = sorted(_prefixes.keys())
        maxlen = max((len(k) for k in keys))
        for k in keys:
            print ("{prefix:{width}} {ns}".format(
                prefix=k,
                width=maxlen,
                ns=_prefixes[k]))

    @magic_arguments()
    @argument('name', nargs=1, type=str,
              help="remove an item from our default namespaces")
    @line_magic
    def delns(self, line=None):
        args = parse_argstring(self.delns, line)
        if args.name is None:
            raise UsageError("Specify what to delete")

        name = args.name[0]
        if name in _prefixes:
            del _namespaces[self._prefixes[name]]
            del _prefixes[name]
        elif name in _namespaces:
            del _prefixes[self._namespaces[name]]
            del _namespaces[name]
        else:
            raise UsageError("%s was not found in our namespace cache" % (
                name,))
        
    @magic_arguments()
    @argument('-D', '--data', default=None, type=str,
              help="Add RDF Data source URI")
    @argument('-p', '--protocol', type=str, default=None,
              help="Call a SPARQL HTTP Protocol at service URI")
    @argument('-m', '--model', type=str, default=None,
              help="Specify a model to use")
    @argument('--output', type=str,
              default=None,
              help="Specifiy variable to hold output")
    @line_cell_magic
    def roqet(self, line, cell):
        """Call libRDF roqet utility"""
        pass

    @magic_arguments()
    @argument('-m', '--model', default=None,
              help="use specified variable as the model to store "\
                   "intermediate results in.")               
    @argument('-o', '--output', type=str, default=None,
              help="Specifiy variable to hold output")
    @cell_magic
    def sparql(self, line, cell=None):
        arg = parse_argstring(self.sparql, line)

        sources = []
        if cell is not None:
            sources, cell = extract_froms(cell)
        if arg.model is None and len(sources) == 0:
            raise UsageError("Please specify a source to query against.")

        if arg.model is not None:
            model = self.shell.user_ns.get(arg.model)
            if not isinstance(model, RDF.Model):
                raise ValueError("Model needs to be RDF.Model")
        else:
            model = make_temp_model()

        for source in sources:
            if source.startswith("tracker:"):
                raise NotImplemented("Tracker queries not implemented yet")
            else: 
                load_source(model, source)

        body = prepare_query(cell)
        query = RDF.SPARQLQuery(body)
        results = LibRdfResults(query.execute(model))

        if arg.output is None:
            return results
        else:
            self.shell.user_ns[arg.output] = results

def extract_froms(cell, remove=True):
    """Extract from statements from sparql query
    librdf doesn't actually use the froms.

    if remove is true, remove the from statements from the query
    returns ([url, url], query)
    """
    from_re = re.compile(
        "from <(?P<url>[A-Za-z0-9!@#$%^&*()-_\\|\'\"/?\]\[{}+=]+)>",
        re.IGNORECASE)
    froms = []
    match = from_re.search(cell)
    while match is not None:
        froms.append(match.group('url'))
        if remove:
            cell = from_re.sub('', cell, 1)
        match = from_re.search(cell)
    return froms, cell

def prepare_query(cell):
    """Add additional our namespaces to head of query
    """
    query = []
    template = "PREFIX {prefix}: <{url}>"
    for prefix, namespace in _prefixes.items():
        query.append(template.format(prefix=prefix, url=namespace))
    query.append(cell)
    return os.linesep.join(query)
        
def make_temp_model():
    """Make a scratch model
    """
    s = RDF.MemoryStorage()
    m = RDF.Model(s)
    return m

def load_source(model, source):
    url = urlparse(source)
    if url.scheme is None:
        source = 'file://'+os.path.abspath(source)
        url = urlparse(source)
    if url.scheme in ('http', 'https'):
        # remote,
        stream = urllib.urlopen(source)
        content_type = stream.headers.get('content-type')
        if stream.code == 200:
            parser = guess_parser(content_type, url.path)

    elif url.schme in ('file'):
        # local
        if not os.path.exists(url.path):
            raise IOError("File %s does not exist" % (url.path,))
        stream = open(url.path, 'r')
        parser = guess_parser(None, url.path)

    body = stream.read()
    stream.close()
    parser.parse_string_into_model(model, body, source)
    
def guess_parser(content_type, pathname):
    name = guess_parser_name(content_type, pathname)
    return RDF.Parser(name=name)

def guess_parser_name(content_type, pathname):
    if content_type.startswith('application/rdf+xml'):
        return 'rdfxml'
    elif content_type.startswith('application/x-turtle'):
        return 'turtle'
    elif content_type.startswith('text/html'):
        return 'rdfa'
    elif content_type is None or content_type.startswith('text/plain'):
        return guess_parser_by_extension(pathname)

def guess_parser_name_by_extension(pathname):
    _, ext = os.path.splitext(pathname)
    if ext in ('.xml', '.rdf'):
        return 'rdfxml'
    elif ext in ('.html',):
        return 'rdfa'
    elif ext in ('.turtle',):
        return 'turtle'
    return 'guess'


_loaded = False
def load_ipython_extension(ip):
    """Load the extension in IPython."""
    global _loaded
    if not _loaded:
        ip.register_magics(SPARQLMagics)
        _loaded = True

