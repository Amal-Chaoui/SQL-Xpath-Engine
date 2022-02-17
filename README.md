# Maxi-project : SQL based XPath engine

### Objective : 
The goal of this project is to develop an engine for evaluating a fragment of XPath queries over an
XML document whose structure has been loaded in an SQLite database.

### Descirption of the files : 
* `load.py` is called with a single argument *xml_file*. This program uses SAX API to implement the functionality of loading the input XML document
into an SQLite database stored in file `xml.db` in the working directory. If the database already exists, the program first deletes its contents, 
thus allowing to test your solution with different XML files.

* `query.py` is called with a single argument *xpath_query*. This program evaluates the given XPath query by compiling them into SQL queries
and running them over the XML document stored in the SQLite database. 
It returns on the standard output (e.g., print) the node ids (one per line) of the nodes selected by the input query. 

* `xpath.py` defines the XPath parser used in this project.

* `unit_tests.py` and `unit_tests.sh` are provided to test the XPATH engine on a given `test.xml` XML document. 

### Recovering the project from Github : 
Create a directory

    $ mkdir git-xpath-engine  
    $ cd git-xpath-engine 
    
Link to the repository of the project

    $ git clone https://github.com/Amal-Chaoui/SQL-Xpath-Engine
    $ cd SQL-Xpath-Engine  

Pull changes from the remote repository :

    $ git pull
    
You can run the test in the `unit_tests.py` file by using the following command : 

    $ python3 unit_tests.py
