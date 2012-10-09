import rdfm
from IPython.core.interactiveshell import InteractiveShell

shell = InteractiveShell()
magic = rdfm.SPARQLMagics(shell)
magic.addns("libns http://jumpgate.caltech.edu/wiki/LibraryOntology#")
magic.addns("htslib http://jumpgate.caltech.edu/library/")
magic.addns("htsflow http://jumpgate.caltech.edu/flowcell/")
#results = magic.sparql('http://jumpgate.caltech.edu/library/12415/',
#                      'select ?s ?p ?o where { ?s ?p ?o .}')

results = magic.sparql('http://jumpgate.caltech.edu/library/?affiliations__id__exact=37 http://jumpgate.caltech.edu/library/?affiliations__id__exact=69 http://jumpgate.caltech.edu/library/?affiliations__id__exact=59',
                       'select ?s ?p ?o where { ?s ?p ?o . }')
print str(results)

print results._repr_html_()
