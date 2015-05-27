rdfmagic
========

Introduction
------------

I had been doing a lot of work using `librdf`_
and wanted a way to easily browse tablular results of 
queries.

So I wrote this.


Prefixes
--------

There's a few magics to manipulate a dictionary of default prefixes
that will be added to sparql queries.

%lsns
  show the list of current prefix to url mappings

%addns prefix url
  defines prefix for the specified url. this is equivalent
  to having done ``PREFIX prefix: <url>`` at the start of your sparql query.
  (Other than the prefixes are also used to shorten output.

%delns prefix
  removes a prefix from the dictionary of default prefixes

%%sparql 
  issues a sparql query. Providing at least a model or a source is required.
  
    -m --model <arg>
        specify model variable to run query against. If no model is set,
        it will use a new temporary memory model
    -s --source <arg>
        add source url to pre-load data from.
    -o --output <arg>
        specify variable to store result of query in
    -c --count
        display how many triples were returned

%load_source [source]*
  load a list of sources into a model

    -m --model <arg>
        model name to store triples in
    source
        list of locations to load triples from
    
%save_model filename
  serialize model in filename
  
  -m --model
      model to store.
  -f --format
      format to serialize model in (turtle, rdf/xml, etc)
  
  
.. _librdf: http://librdf.org/
