# this file  will handle loading the provided xml file into an SQLite Database
import sys
import xml.sax
import sqlite3

from collections import deque

	
class SAXHandler(xml.sax.ContentHandler):

	def __init__(self):
		self.db = None
		self.c = None
		
		self.id = 0						     # current id of the element
		self.parent_stack = deque()          # parent stack 
		self.parent_stack.append(None)
		
		self.stack_start = deque()		     # stack of entry times to a new element
		self.count =0					     # counts of entries and exits
		
		
	def startDocument(self):
		self.db = sqlite3.connect('xml.db')  # connection to 'xml.db'
		self.c = self.db.cursor()
		
		# Drop Table Nodes and existing indexes 
		self.c.execute('DROP TABLE IF EXISTS Nodes;')
		self.c.execute('DROP INDEX IF EXISTS Index1;')
		self.c.execute('DROP INDEX IF EXISTS Index2;')
		self.c.execute('DROP INDEX IF EXISTS Index3;')

		# Creation of Nodes table
		self.c.execute('CREATE TABLE Nodes (ID INT, Name TEXT, ID_parent INT, Interval_start INT, Interval_end INT);')
		
		
	def startElement(self, xml_name, xml_attrs):
		self.parent_stack.append(self.id)	 # updating parent_stack
		 
		self.stack_start.append(self.count)  # updating start times stack
		self.count += 1 					 
		
		self.id +=1							 # updating id of the current element 
			
	
	def characters(self, text):
		pass
		
		
	def endElement(self, xml_name):
		self.parent_stack.pop()
		
		# id of the current_element  = self.id - (distance of interval_encoding-1)/2 - 1
		start = self.stack_start[-1]
		end = self.count
		real_id= self.id - int((end-start-1)/2)-1
		
		self.c.execute('INSERT INTO Nodes VALUES (?,?,?,?,?);', 
					(real_id, xml_name, self.parent_stack[-1], start, end))

		self.stack_start.pop()              # delete the last start time 
		self.count += 1
		
		
	def endDocument(self):
		# adding indexes 
		self.c.execute('CREATE INDEX IF NOT EXISTS Index1 ON Nodes(ID);')
		self.c.execute('CREATE INDEX IF NOT EXISTS Index2 ON Nodes(ID, ID_parent);')
		self.c.execute('CREATE INDEX IF NOT EXISTS Index3 ON Nodes(ID_parent, Name);')

		#self.c.execute('CREATE INDEX IF NOT EXISTS Index1 ON Nodes(ID_parent);')
		#self.c.execute('CREATE UNIQUE INDEX IF NOT EXISTS Index2 ON Nodes(ID, Interval_start, Interval_end);')		
		
		self.db.commit()
		self.db.close()
		
		
def run(xml_file_name):
	parser = xml.sax.make_parser()
	handler = SAXHandler()
	parser.setContentHandler(handler)
	parser.parse(open(xml_file_name, 'r'))


def load(xml_file):
	run(xml_file)
	
	
if __name__ == '__main__':
	import resource
	import sys
	
	if len(sys.argv) !=2:
		print("Number of arguments invalid!")
	
	load(sys.argv[1])
	
	# Time and RAM usage
	res = resource.getrusage(resource.RUSAGE_SELF)
	print("User time %.3f sec"%(res.ru_utime,))
	print("Maximum %.2fMb"%(res.ru_maxrss/1024/1024,))
