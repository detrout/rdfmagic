import unittest
import RDF

import rdfm
from IPython.core.interactiveshell import InteractiveShell

class TestRDFMagic(unittest.TestCase):
    def setUp(self):
        self.shell = InteractiveShell()
        self.magic = rdfm.SPARQLMagics(self.shell)
        for ns_cmd in [
            "libns http://jumpgate.caltech.edu/wiki/LibraryOntology#",
            "htslib http://jumpgate.caltech.edu/library/",
            "htsflow http://jumpgate.caltech.edu/flowcell/"]:
            self.magic.addns(ns_cmd)

    def test_sources_literal(self):
        results = self.magic.sparql(
            '-s http://jumpgate.caltech.edu/library/12415/',
            """select ?s ?p ?o
               where { ?s ?p ?o . }""")
        self.assertEqual(len(results), 28)
        self.assertEqual(set(results[0].keys()), {'s', 'p', 'o'})

        self.assertTrue(len(str(results)) > 0)
        self.assertTrue(len(str(results._repr_html_())) > 0)

    def test_sources_str(self):
        self.shell.user_ns['url'] = 'http://jumpgate.caltech.edu/library/12415/'
        results = self.magic.sparql(
            '-s url',
            """select ?s ?p ?o
               where { ?s ?p ?o . }""")
        self.assertEqual(len(results), 28)
        self.assertEqual(set(results[0].keys()), {'s', 'p', 'o'})

        self.assertTrue(len(str(results)) > 0)
        self.assertTrue(len(str(results._repr_html_())) > 0)

    def test_sources_list(self):
        self.shell.user_ns['url'] = ['http://jumpgate.caltech.edu/library/12415/']
        results = self.magic.sparql(
            '-s url',
            """select ?s ?p ?o
               where { ?s ?p ?o . }""")
        self.assertEqual(len(results), 28)
        self.assertEqual(set(results[0].keys()), {'s', 'p', 'o'})

        self.assertTrue(len(str(results)) > 0)
        self.assertTrue(len(str(results._repr_html_())) > 0)

    def test_query(self):
        results = self.magic.sparql(
            '',
            """select ?s ?p ?o
               from <http://jumpgate.caltech.edu/library/12415/>
               where { ?s ?p ?o . }""")
        self.assertEqual(len(results), 28)
        self.assertEqual(set(results[0].keys()), {'s', 'p', 'o'})

        self.assertTrue(len( str(results)) > 0)
        self.assertTrue(len(str(results._repr_html_())) > 0)

    def test_extract_froms(self):
        q = "select ?s from <http://f.org/b+3?q=asdf#foo> where"
        froms, new_q = rdfm.extract_froms(q)
        self.assertEqual(new_q, "select ?s  where")

        q = 'select from <abc> from named <def> from <gef> where'
        froms, new_q = rdfm.extract_froms(q)
        self.assertEqual(new_q, "select  from named <def>  where")

    def test_load_source_magic(self):
        self.shell.user_ns['model'] = RDF.Model(RDF.MemoryStorage())
        self.magic.load_source('-m model http://jumpgate.caltech.edu/library/12415/')
        self.assertEqual(len(self.shell.user_ns['model']), 28)


    def test_guess_parser(self):
        self.assertEqual(rdfm.guess_parser_name(None, "diane.ttl"), 'turtle')
        self.assertEqual(rdfm.guess_parser_name(None, "diane.turtle"), 'turtle')
        self.assertEqual(rdfm.guess_parser_name(None, "diane.html"), 'rdfa')
        self.assertEqual(rdfm.guess_parser_name(None, "diane.xhtml"), 'rdfa')
        self.assertEqual(rdfm.guess_parser_name(None, "diane.xml"), 'rdfxml')
        self.assertEqual(rdfm.guess_parser_name(None, "diane.rdf"), 'rdfxml')

        self.assertEqual(rdfm.guess_parser_name('application/rdf+xml', 'foo'),
                         'rdfxml')
        self.assertEqual(rdfm.guess_parser_name('application/x-turtle', 'foo'),
                         'turtle')
        self.assertEqual(rdfm.guess_parser_name('text/html', 'http://example.org/f.ttl'),
                         'rdfa')
        self.assertEqual(rdfm.guess_parser_name('image/jpg', 'http://example.org/f.ttl'),
                         'guess')


if __name__ == "__main__":
    unittest.main()
