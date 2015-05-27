# -*- coding: utf-8 -*-
# Copyright (C) 2014 Diane Trout
#
# This package is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License Version 2.1
# as published by the Free Software Foundation or any newer version.

# This package is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License Version 2.1 for more details.

# You should have received a copy of the GNU Lesser General Public
# License Version 2.1 along with this package; if not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
# MA 02110-1301 USA

import os
import shutil
import tempfile
import unittest
import RDF

import rdfmagic
from IPython.core.interactiveshell import InteractiveShell

testdata = '''
@base <http://example.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix rel: <http://www.perceive.net/schemas/relationship/> .

<#green-goblin>
    rel:enemyOf <#spiderman> ;
    a foaf:Person ;    # in the context of the Marvel universe
    foaf:name "Green Goblin" .

<#spiderman>
    rel:enemyOf <#green-goblin> ;
    a foaf:Person ;
    foaf:name "Spiderman", "Человек-паук"@ru .
'''


class TestRDFMagic(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp(prefix='test_rdfm_')
        self.tempfile = os.path.join(self.tempdir, 'spiderman.ttl')
        self.tempurl = 'file://' + self.tempfile
        with open(self.tempfile, 'w') as outstream:
            outstream.write(testdata)

        self.shell = InteractiveShell()
        self.magic = rdfmagic.SPARQLMagics(self.shell)
        for ns_cmd in [
                "libns http://jumpgate.caltech.edu/wiki/LibraryOntology#",
                "htslib http://jumpgate.caltech.edu/library/",
                "htsflow http://jumpgate.caltech.edu/flowcell/"]:
            self.magic.addns(ns_cmd)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_sources_literal(self):
        results = self.magic.sparql(
            '-s file://' + self.tempurl,
            """select ?s ?p ?o
               where { ?s ?p ?o . }""")
        self.assertEqual(len(results), 7)
        self.assertEqual(set(results[0].keys()), {'s', 'p', 'o'})

        self.assertTrue(len(str(results)) > 0)
        self.assertTrue(len(str(results._repr_html_())) > 0)

    def test_sources_str(self):
        self.shell.user_ns['url'] = self.tempurl
        results = self.magic.sparql(
            '-s url',
            """select ?s ?p ?o
               where { ?s ?p ?o . }""")
        self.assertEqual(len(results), 7)
        self.assertEqual(set(results[0].keys()), {'s', 'p', 'o'})

        self.assertTrue(len(str(results)) > 0)
        self.assertTrue(len(str(results._repr_html_())) > 0)

    def test_sources_list(self):
        self.shell.user_ns['url'] = [self.tempurl]
        results = self.magic.sparql(
            '-s url',
            """select ?s ?p ?o
               where { ?s ?p ?o . }""")
        self.assertEqual(len(results), 7)
        self.assertEqual(set(results[0].keys()), {'s', 'p', 'o'})

        self.assertTrue(len(str(results)) > 0)
        self.assertTrue(len(str(results._repr_html_())) > 0)

    def test_query(self):
        results = self.magic.sparql(
            '',
            """select ?s ?p ?o
               from <{}>
               where {{ ?s ?p ?o . }}""".format(self.tempurl))
        self.assertEqual(len(results), 7)
        self.assertEqual(set(results[0].keys()), {'s', 'p', 'o'})

        self.assertTrue(len( str(results)) > 0)
        self.assertTrue(len(str(results._repr_html_())) > 0)

    def test_extract_froms(self):
        q = "select ?s from <http://f.org/b+3?q=asdf#foo> where"
        froms, new_q = rdfmagic.extract_froms(q)
        self.assertEqual(new_q, "select ?s  where")

        q = 'select from <abc> from named <def> from <gef> where'
        froms, new_q = rdfmagic.extract_froms(q)
        self.assertEqual(new_q, "select  from named <def>  where")

    def test_load_source_magic(self):
        self.shell.user_ns['model'] = RDF.Model(RDF.MemoryStorage())
        self.magic.load_source('-m model '+self.tempurl)
        self.assertEqual(len(self.shell.user_ns['model']), 7)

    def test_guess_parser(self):
        self.assertEqual(rdfmagic.guess_parser_name(None, "diane.ttl"), 'turtle')
        self.assertEqual(rdfmagic.guess_parser_name(None, "diane.turtle"), 'turtle')
        self.assertEqual(rdfmagic.guess_parser_name(None, "diane.html"), 'rdfa')
        self.assertEqual(rdfmagic.guess_parser_name(None, "diane.xhtml"), 'rdfa')
        self.assertEqual(rdfmagic.guess_parser_name(None, "diane.xml"), 'rdfxml')
        self.assertEqual(rdfmagic.guess_parser_name(None, "diane.rdf"), 'rdfxml')

        self.assertEqual(rdfmagic.guess_parser_name('application/rdf+xml', 'foo'),
                         'rdfxml')
        self.assertEqual(rdfmagic.guess_parser_name('application/x-turtle', 'foo'),
                         'turtle')
        self.assertEqual(rdfmagic.guess_parser_name('text/html', 'http://example.org/f.ttl'),
                         'rdfa')
        self.assertEqual(rdfmagic.guess_parser_name('image/jpg', 'http://example.org/f.ttl'),
                         'guess')


def suite():
    from unittest import TestSuite, defaultTestLoader
    suite = TestSuite()
    suite.addTests(defaultTestLoader.loadTestsFromTestCase(TestRDFMagic))
    return suite

if __name__ == "__main__":
    unittest.main()
