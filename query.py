import xpath
import engine
import sqlite3
import sys


def query(xpath_query):
	q = xpath.parse(xpath_query)             # parsed xpath query
	db = sqlite3.connect('xml.db')           # connection to 'xml.db'
	return engine.execute_query(db, q)       # return the result (the corresponding set of nodes )
	
	
if __name__ == "__main__":	
	if len(sys.argv)!=2:
		print("Invalid number of arguments!")
		
	result = query(sys.argv[1])
	for x in result:
		print(x)

