import ply.lex as lex
import ply.yacc as yacc
import difflib



# XPath AXES 
axes = [
    "ancestor", 
    "ancestor-or-self", 
    "child", 
    "descendant", 
    "descendant-or-self", 
    "following", 
    "following-sibling", 
    "parent", 
    "preceding", 
    "preceding-sibling", 
    "self"
]

# LEXER DEFINITION
states = (
    ('string','exclusive'),
)

reserved = {
    'and':'AND',
    'or':'OR',
    'not':'NOT',
}

tokens = [
    'DBL_COLON',
    'STAR',
    'BAR',
    'SLASH',
    'OPEN_B',
    'CLOSE_B',
    'OPEN_P',
    'CLOSE_P',
    'EQ',
    'NEQ',
    'NAME',
    'STRING',
] + list(reserved.values())


def t_NAME(t):
    r'[a-zA-Z_][-a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'NAME')
    return t

t_DBL_COLON = r'::'
t_BAR = r'\|'
t_OPEN_B = r'\['
t_CLOSE_B = r'\]'
t_OPEN_P = r'\('
t_CLOSE_P = r'\)'
t_SLASH = r'/'
t_STAR = r'\*'
t_EQ = r'='
t_NEQ = r'!='

t_ignore = ' \t\n\r\f\v'

quote_symbol = None
def t_QUOTE(t): 
    r'\'|"'
    global quote_symbol
    quote_symbol = t.value
    t.lexer.begin('string')
t_string_ignore = ''

string_acc = ''
def t_string_STRING(t):
    r"[^'\"]*('|\")"
    global string_acc
    if t.value[-1] == quote_symbol:
        t.value = string_acc + t.value[:-1]
        string_acc = ''
        t.lexer.begin('INITIAL')
        return t
    else:
        string_acc += t.value


def t_ANY_error(t):
    print('Error in line',t.lineno,'position',t.lexpos)
    print('>>>',t.value[:25],'...')
    exit(1)

# GRAMMAR DEFINITION

def p_xpath_bar(p):
    '''xpath : path BAR xpath'''
    p[0] = {'kind' : 'xpath_union',
            'xpath1': p[1],
            'xpath2': p[3]}
def p_xpath_path(p):
    '''xpath : path'''
    p[0] = p[1]

def p_path_slash(p):
    '''path : SLASH rel_path'''
    p[0] = {'kind': 'xpath_absolute',
            'xpath': p[2]}

def p_path_rel_path(p):
    '''path : rel_path'''
    p[0] = p[1]

def p_rel_path_slash(p):
    '''rel_path : step SLASH rel_path'''
    p[0] = {'kind' : 'xpath_join',
            'step' : p[1],
            'xpath': p[3]}

def p_rel_path_step(p):
    '''rel_path : step'''
    p[0] = p[1]

def p_rel_path_xpath(p):
    '''rel_path : OPEN_P xpath CLOSE_P'''
    p[0] = p[2]

def p_step(p):
    '''step : NAME DBL_COLON node_test
            | NAME DBL_COLON node_test OPEN_B filter_expr CLOSE_B'''
    if p[1] not in axes:
        print('Error: unknown axis "'+p[1]+'".')
        matches = difflib.get_close_matches(p[1], axes)
        if matches:
            print('Did you mean "' + '" or "'.join(matches) + '"?')
        exit(1)
        
    p[0] = {'kind'     : 'xpath_step',
            'axis'     : p[1],
            'node_test': p[3]}
    # TODO: check that good axis are used
    if len(p) > 4:
        p[0]['filter'] = p[5]

def p_node_test(p):
    '''node_test : STAR
                 | NAME
                 | NAME OPEN_P CLOSE_P'''
    if p[1] == t_STAR:
        p[0] = '*'
    elif len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = 'text()'
        if p[1] != 'text':
            print('Error: unknown kind of node selection "'+p[1]+p[2]+p[3]+'". '+
                  'Did you mean "text()"?')
            exit(1)

def p_filter_expr_or(p):
    '''filter_expr : filter_conj OR filter_expr'''
    p[0] = {'kind'   : 'filter_or',
            'filter1': p[1],
            'filter2': p[3]}

def p_filter_expr_conj(p):
    '''filter_expr : filter_conj'''
    p[0] = p[1]

def p_filter_conj_and(p):
    '''filter_conj : filter_neg AND filter_conj'''
    p[0] = {'kind'   : 'filter_and',
            'filter1': p[1],
            'filter2': p[3]}

def p_filter_conj_neg(p):
    '''filter_conj : filter_neg'''
    p[0] = p[1]

def p_filter_neg_not(p):
    '''filter_neg : NOT filter_neg'''
    p[0] = {'kind'  : 'filter_not',
            'filter': p[2]}

def p_filter_neg_atom(p):
    '''filter_neg : filter_atom'''
    p[0] = p[1]

def p_filter_neg_expr(p):
    '''filter_neg : OPEN_P filter_expr CLOSE_P'''
    p[0] = p[2]

def p_filter_atom_exists(p):
    '''filter_atom : xpath'''
    p[0] = {'kind' : 'filter_exists',
            'xpath': p[1]}

def p_filter_atom_op_xpath(p):
    '''filter_atom : xpath operator xpath'''
    p[0] = {'kind'    : 'filter_compare_xpath',
            'operator': p[2], 
            'xpath1'  : p[1],
            'xpath2'  : p[3]}

def p_filter_atom_op_const(p):
    '''filter_atom : xpath operator const
                   | const operator xpath'''
    p[0] = {'kind'    : 'filter_compare_const',
            'operator': p[2], 
            'xpath'   : None,
            'const'   : None}
    if type(p[1]) in [float,int,str]:
        p[0]['xpath'] = p[3]
        p[0]['const'] = p[1]
    else:
        p[0]['xpath'] = p[1]
        p[0]['const'] = p[3]

def p_operator(p):
    '''operator : EQ 
                | NEQ'''
    p[0] = p[1]

def p_const(p):
    '''const : STRING'''
    p[0] = p[1]

def p_error(p):
    print("Syntax error in input!")    
    exit(1)

# Main methods 

lexer = lex.lex()
parser = yacc.yacc()

def parse(query_string,debug=False):
    query = parser.parse(query_string,debug)
    if not query:
        print('Error parsing query string',query_string)
        exit(1)
    return query

# Utilities 

def to_pretty_str(p):
    acc = []
    _aux1(p,acc,'','')
    return '\n'.join(acc)

def _aux1(p, acc, first_indent, indent):
    
    if type(p) != dict:
        acc.append(first_indent + ' ' + p)
        return 

    acc.append(first_indent + ' ' + p['kind'])
        
    if p['kind'] == 'xpath_union':
        _aux1(p['xpath1'],acc,indent+' |- xpath1:',indent+' |         ')
        _aux1(p['xpath2'],acc,indent+' |- xpath2:',indent+'           ')
    elif p['kind'] == 'xpath_absolute':
        _aux1(p['xpath'],acc,indent+' |- xpath:',indent+'          ')
    elif p['kind'] == 'xpath_join':
        _aux1(p['step'],acc,indent+' |- step:',indent+' |       ')
        _aux1(p['xpath'],acc,indent+' |- xpath:',indent+'          ')
    elif p['kind'] == 'xpath_step':
        acc.append(indent + ' ' + '|- axis:' + ' ' + p['axis'])
        acc.append(indent + ' ' + '|- node_test:' + ' ' + p['node_test'])
        if 'filter' in p:
            _aux1(p['filter'],acc,indent+' |- filter:',indent+'           ')
    elif p['kind'] in ['filter_or','filter_and']:
        _aux1(p['filter1'],acc,indent+' |- filter1:',indent+' |          ')
        _aux1(p['filter2'],acc,indent+' |- filter2:',indent+'            ')
    elif p['kind'] == 'filter_not':
        _aux1(p['filter'],acc,indent+' |- filter:',indent+'           ')
    elif p['kind'] == 'filter_exists':
        _aux1(p['xpath'],acc,indent+' |- xpath:',indent+'          ')
        pass
    elif p['kind'] == 'filter_compare_xpath':
        acc.append(indent + ' ' + '|- operator:'+ ' ' +p['operator'])
        _aux1(p['xpath1'],acc,indent+' |- xpath1:',indent+' |         ')
        _aux1(p['xpath2'],acc,indent+' |- xpath2:',indent+'           ')
    else: #p['kind'] == 'filter_compare_const':
        acc.append(indent+ ' ' +'|- operator:'+ ' ' +p['operator'])
        _aux1(p['xpath'],acc,indent+' |- xpath:',indent+' |        ')
        _aux1(p['const'],acc,indent+' |- const:',indent+'          ')



def to_str(p):
    if type(p) != dict:
        return str(p)

    if p['kind'] == 'xpath_union':
        return to_str(p['xpath1']) + " | " + to_str(p['xpath2'])
    elif p['kind'] == 'xpath_absolute':
        return "/" + to_str(p['xpath'])
    elif p['kind'] == 'xpath_join':
        return to_str(p['step']) + "/" + to_str(p['xpath'])
    elif p['kind'] == 'xpath_step':
        if 'filter' not in p:
            return p['axis'] + "::" + p['node_test']
        else:
            return p['axis'] + "::" + p['node_test'] + "[" + to_str(p['filter']) + "]"
    elif p['kind'] == 'filter_and':
        return "(" + to_str(p['filter1']) + " and " + to_str(p['filter2']) +")"
    elif p['kind'] == 'filter_or':
        return "(" + to_str(p['filter1']) + " or " + to_str(p['filter2']) + ")"
    elif p['kind'] == 'filter_not':
        return "not (" + to_str(p['filter']) +")"
    elif p['kind'] == 'filter_exists':
        return "(" + to_str(p['xpath']) + ")"
    elif p['kind'] == 'filter_compare_xpath':
        return to_str(p['xpath1']) + p['operator'] + to_str(p['xpath2'])
    else: #p['kind'] == 'filter_compare_const':
        return to_str(p['xpath']) + p['operator'] + "'" + to_str(p['const']) + "'"



if __name__ == '__main__':
    #query_string = '/child::a[child::text() = "text1" and following-sibling::*]/parent::b'
    query_string ='/child::a[child::b and child::a]'
    #query_string = '/descendant::c[child::text()!=child::a/child::text()]'
    #query_string = '/descendant::b/child::c[child::text()]'
    print('Lexing',query_string)
    lexer.input(query_string)
    while True:
        tok = lexer.token()
        if not tok:
            break      # No more input
        print(tok)
    query = parser.parse(query_string)
    print("XPath")
    print(to_str(query))
    print("AST")
    print(to_pretty_str(query))

