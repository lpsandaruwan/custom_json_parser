import argparse
import pprint

import ply.lex as lex
import ply.yacc as yacc


# Parsing error definitions
class ParserError(Exception): pass


def p_object(p):
    """object : LBRACKET members RBRACKET
              | LBRACKET RBRACKET"""
    p[0] = {}
    if len(p) == 4:
        for item in p[2]:
            p[0][item[0]] = item[1]


def p_members(p):
    """members : pair
             | pair COMMA members"""
    p[0] = [p[1]]
    if len(p) == 4:
        for item in p[3]:
            p[0].append(item)


def p_pair(p):
    """pair : STRING COLON value"""
    p[0] = [p[1], p[3]]


def p_array(p):
    """array : LSQBRACKET RSQBRACKET
        | LSQBRACKET elements RSQBRACKET"""
    p[0] = []
    if len(p) == 4:
        for item in p[2]:
            p[0].append(item)


def p_elements(p):
    """elements : value
        | value COMMA elements"""
    p[0] = [p[1]]
    if len(p) == 4:
        for item in p[3]:
            p[0].append(item)


def p_value(p):
    """value : STRING
           | NUMBER
           | object
           | array
           | TRUE
           | FALSE
           | NULL"""
    p[0] = p[1]


# Error rule for parsing errors
def p_error(p):
    raise ParserError(p)


# Exception to handle lexing errors
class LexerError(Exception): pass


# List of token names
tokens = [
    'STRING',
    'NUMBER',
    'COMMA',
    'COLON',
    'TRUE',
    'FALSE',
    'NULL',
    'LBRACKET',
    'RBRACKET',
    'LSQBRACKET',
    'RSQBRACKET'
]

# --> Defining regular expression rules ---

t_ignore = ' \t\n'
t_COMMA = r','
t_COLON = r':'
t_LBRACKET = r'\{'
t_RBRACKET = r'\}'
t_LSQBRACKET = r'\['
t_RSQBRACKET = r'\]'


def t_STRING(t):
    r'"(([^"\\])|(\\["\\\/bfnrt])|(\\u[0-9a-f]{4}))*"'
    t.value = t.value[1:-1]  # Remove quotation marks
    return t


def t_NUMBER(t):
    r'\-?(0|([1-9][0-9]*))(\.[0-9]*)?([eE][\+\-]?[0-9]*)?'
    try:
        t.value = int(t.value)
    except:
        t.value = float(t.value)
    return t


def t_TRUE(t):
    r'true'
    t.value = True
    return t


def t_FALSE(t):
    r'false'
    t.value = False
    return t


def t_NULL(t):
    r'null'
    t.value = None
    return t


# Error rule for lexing errors
def t_error(t):
    raise LexerError(t)


def parse_file(file_path):
    file_obj = open(file_path)
    file = file_obj.read()
    try:
        result = parser.parse(file)
        print("".join(["JSON parser succeeded: JSON Syntax validation successful in ", file_path]))
        return result
    except LexerError as error:
        print("".join(["JSON parser Failed: Parser error around character index: ", str(error.args[0].lexpos), ": ",
                       error.args[0].value[0]]))
    except ParserError as error:
        if error.args[0]:
            print("".join(["JSON parser Failed: Parser error around character index: ", str(error.args[0].lexpos), ": ",
                           error.args[0].value]))
        else:
            print('Parsing Failed: ParserError at EOF')
    finally:
        file_obj.close()


def print_dict(dict_obj):
    pprint.pprint(dict_obj)


lexer = lex.lex()  # Build the lexer
parser = yacc.yacc()  # Build the parser

arg_parser = argparse.ArgumentParser(description='JSON format validator/Parser.')
arg_parser.add_argument('file')
arg_parser.add_argument(
    '-p',
    '--print',
    action='store_true',
    help='Pretty print JSON file.')
arg_parser.add_argument(
    '-k',
    '--key',
    help='Obtain value for the provided key.')

args = arg_parser.parse_args()

json_parser_result = None
if args.file:
    json_parser_result = parse_file(args.file)
    if args.print and json_parser_result is not None:
        print("")
        print_dict(json_parser_result)
    if args.key is not None and args.key != '':
        if args.key in json_parser_result.keys():
            print("")
            print("".join(["Value for ", args.key, ":"]))
            print_dict(json_parser_result[args.key])
        else:
            print("".join(["Requested JSON key ", args.key, " does not exists in ", args.file]))
else:
    print("JSON parser Failed: Invalid file path.")
