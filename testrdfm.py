import unittest

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

if __name__ == "__main__":
    unittest.main()
