# Maxi-project : SQL based XPath engine

### Objective : 
The goal of this project is to develop an engine for evaluating a fragment of XPath queries over an
XML document whose structure has been loaded in an SQLite database.

### Requirements : 


### Descirption of the files : 
* `load.py` is called with a single argument *xml_file*. This program uses SAX API to implement the functionality of loading the input XML document
into an SQLite database stored in file `xml.db` in the working directory. If the database already exists, the program first deletes its contents, 
thus allowing to test your solution with different XML files.

* `query.py` is called with a single argument *xpath_query*. This program evaluates the given XPath query by compiling them into SQL queries
and running them over the XML document stored in the SQLite database. 
It returns on the standard output (e.g., print) the node ids (one per line) of the nodes selected by the input query. 


