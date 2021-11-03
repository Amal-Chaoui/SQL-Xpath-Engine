import xpath
import sqlite3

# 					-------------- Remarks -------------- 
# The implementation of the following functions suppose the existence of some global variables : 
# 		* counter 	  : counts the depth of the query (number of elementary queries)
#		* query  	  : holds the overall SQL query equivalent to the passed xpath query 
#       * select_node : keeps track of the index of node to select.
# 						This is particularly relevant when using filters or more complex form of xpath queries 
# 		* in_filter   : keeps track of the current state of the query (whether inside a filter) and helps update 
# 						the select_node accordingly 
# 					-------------------------------------




#    -------------- axis_step --------------   
def axis_step(a, prev, node_test):
	""" Updates a global variable 'query' according to the type of axis (a) and 
		the index of the previous and current tables with the corresponding SQL query

	Parameters
	----------
	a : string
		axis type

	prev : int
		index of the previous joined table 
	node_test : string
		- '*' : to select all nodes 
		- 'label' = select nodes with Name (label) = 'label'
	"""
	assert a in xpath.axes
	
	global counter
	global query

	cur_tab = "n"+str(counter)           # name of the current table 
	prev_tab = "n"+str(prev)             # name of the previous table 

	if prev == 0:
		query += prev_tab+".ID=0 AND "   # handling the case of root element 
	
	if node_test == '*':				 # select all nodes 
		label = "Null is Null"
	else : 								 # select nodes with the given label
		label = cur_tab+".Name = '"+str(node_test)+"'"

	
	if a == "child":
		query+= cur_tab+".ID_parent ="+prev_tab+".ID AND "+label+" AND "

	elif a == "self":
		query+=cur_tab+".ID ="+prev_tab+ ".ID AND "+label +" AND "
		
	elif a == "parent":
		query+=cur_tab+".ID ="+prev_tab+ ".ID_parent AND "+label +" AND "	
		
	elif a == "descendant":
		query += cur_tab+".Interval_end > "+prev_tab+".Interval_start AND "+cur_tab+".Interval_end < "+prev_tab+".Interval_end AND "+label+" AND "
		
	elif a == "descendant-or-self":
		query += cur_tab+".Interval_end >= "+prev_tab+".Interval_start AND "+cur_tab+".Interval_end <= "+prev_tab+".Interval_end AND "+label+" AND "
		
	elif a == "ancestor":
		query += prev_tab+".Interval_end > "+cur_tab+".Interval_start AND "+prev_tab+".Interval_end < "+cur_tab+".Interval_end AND "+label+" AND "
		
	elif a == "ancestor-or-self":
		query += prev_tab+".Interval_end >= "+cur_tab+".Interval_start AND "+prev_tab+".Interval_end <= "+cur_tab+".Interval_end AND "+label+" AND "
		
	elif a == "following-sibling":
		query += cur_tab+".ID_parent = "+prev_tab+".ID_parent AND "+cur_tab+".ID >"+prev_tab+".ID AND "+label+" AND "
		
	elif a == "preceding-sibling":
		query += cur_tab+".ID_parent = "+prev_tab+".ID_parent AND "+cur_tab+".ID <"+prev_tab+".ID AND "+label+" AND "
		
	else:
		print("Error: Unsupported axis", a)
		exit(1)
		


			
#   -------------- evaluate --------------
def evaluate(q, prev = -1):
	""" Updates the global variable 'query' according to the given xpath query 'q' (after parsing)
		with the corresponding SQL query

	Parameters
	----------
	q : dict
		parsed xpath xquery
	prev : int, optional
		index of the previous joined table, by default -1
	"""
	global counter 
	global select_node
	global in_filter
	global query
	
	if in_filter == 0:					# if outside filter: 
		select_node = counter           # update select_node to the current depth of the query

	if q['kind'] == 'xpath_absolute':
		counter+=1
		evaluate(q['xpath'],  prev+1 ) 
		
	elif q['kind'] == 'xpath_join':
		evaluate(q['step'], prev)
		counter+=1	
		evaluate(q['xpath'], prev+1) 
		
	elif q['kind'] == 'xpath_union':
		query += " ( "
		evaluate(q['xpath1'], prev)
		counter +=1
		query += " NULL IS NULL OR  "
		evaluate(q['xpath2'], prev)
		query+= " NULL IS NULL ) AND  "
		
	elif q['kind'] == 'xpath_step':
		axis_step(q['axis'], prev, q['node_test'])  # call to axis_step
		
		if 'filter' in q:
			in_filter +=1							# entered filter
			counter+=1
			eval_filter(q['filter'],  prev+1)
			in_filter -=1        				    # left filter
			
		
	else:
		print("Error: Unsupported XPath feature", q['kind'])
		
		


#   -------------- eval_filter --------------			
def eval_filter(f, prev):
	""" Updates 'query' string according to the conditions passed in the filter
		with the corresponding SQL query

	Parameters
	----------
	f : dict
		parsed xpath query after entering filter
	prev : int
		index of the previous joined table
	"""
	global counter
	global query
	
	if f['kind'] == 'filter_and':
		eval_filter(f['filter1'], prev) 
		counter +=1
		eval_filter(f['filter2'],prev)
	
	elif f['kind'] == 'filter_exists':
		evaluate(f['xpath'],  prev)
		
	elif f['kind'] == 'filter_or':
		query +=" ( "
		eval_filter(f['filter1'], prev) 
		counter +=1
		query += " NULL IS NULL OR  "
		eval_filter(f['filter2'], prev) 
		query+= " NULL IS NULL ) AND  "
	
	else:
		print("Error: Unsupported XPath filter feature", f['kind'])




#   -------------- execute_query --------------
def execute_query(db, q):
	""" Returns the set of nodes satisfying the parsed xpath query 'q' from the given database reference

	Parameters
	----------
	db : database reference
	
	q : dict
		parsed xpath query

	Returns
	-------
	set
		set of nodes with respect to the given xpath query
	"""
	global counter
	global select_node
	global query
	global in_filter

	# initializing global variables
	counter = 0
	select_node = 0
	query = " WHERE "
	in_filter = 0
	
	evaluate(q)          # evaluating the parsed xpath query 'q'

	selection = ""       # string of selection of joined tables 

	selection +="SELECT n"+str(select_node)+".* FROM Nodes as n"+str(select_node)   # precising the selection table (using select_node)

	for i in range(0, counter+1):
		if i != select_node:
			selection += " JOIN (SELECT * FROM Nodes) as n"+str(i)

	query = selection + query+" NULL IS NULL;"     # final SQL query 

	return {t[0] for t in db.execute(query)}
	




if __name__ == "__main__":
	import xpath
	import sqlite3
	import resource
	
	# defining global variables 
	counter = 0
	select_node = 0
	in_filter = 0
	query = " WHERE "

	db = sqlite3.connect('xml.db')								# connecting ot the database 
	q = xpath.parse('/child::a[child::b/child::c/child::a]')    # xpath query

	result = execute_query(db, q)								# final result

	# Time and RAM consumption 
	res = resource.getrusage(resource.RUSAGE_SELF)
	print("User time %.3f sec"%(res.ru_utime,))
	print("Maximum %.2fMb"%(res.ru_maxrss/1024/1024,))
	


