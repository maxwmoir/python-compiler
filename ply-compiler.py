

import ply.lex as lex
import ply.yacc as yacc
import sys

# Restrictions:
# Integer constants must be short.
# Stack size must not exceed 1024.
# Integer is the only type.
# Logical operators cannot be nested.

# reserved words
reserved = {
    'do': 'DO',
    'else': 'ELSE',
    'end': 'END',
    'if': 'IF',
    'then': 'THEN',
    'while': 'WHILE',
    'read': 'READ',
    'write': 'WRITE',
    'or'   : 'OR',
    'and'  : 'AND',
    'not'  : 'NOT'
}

# all token types
tokens = [
    'SEM', 'BEC', 'LESS', 'EQ', 'GRTR', 'LEQ', 'NEQ', 'GEQ',
    'ADD', 'SUB', 'MUL', 'DIV', 'LPAR', 'RPAR', 'NUM', 'ID'
] + list(reserved.values())


# rules specifying regular expressions and actions

t_SEM = r';'
t_BEC = r':='
t_LESS = r'<'
t_EQ = r'='
t_GRTR = r'>'
t_LEQ = r'<='
t_GEQ = r'>='
t_ADD = r'\+'
t_SUB = r'-'
t_LPAR = r'\('
t_RPAR = r'\)'

t_NEQ = r'!='
t_MUL = r'\*'
t_DIV = r'/'
t_NUM = r'[0-9]+'

def t_ID(t):
    r'[a-z]+'
    t.type = reserved.get(t.value,'ID')
    return t

# rule to track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# rule to ignore whitespace
t_ignore = ' \t'

# error handling rule
def t_error(t):
    print(f"lexical error: illegal character '{t.value[0]}'")
    t.lexer.skip(1)

class Symbol_Table:
    '''A symbol table maps identifiers to locations.'''
    def __init__(self):
        self.symbol_table = {}
    def size(self):
        '''Returns the number of entries in the symbol table.'''
        return len(self.symbol_table)
    def location(self, identifier):
        '''Returns the location of an identifier. If the identifier is not in
           the symbol table, it is entered with a new location. Locations are
           numbered sequentially starting with 0.'''
        if identifier in self.symbol_table:
            return self.symbol_table[identifier]
        index = len(self.symbol_table)
        self.symbol_table[identifier] = index
        return index

class Label:
    def __init__(self):
        self.current_label = 0
    def next(self):
        '''Returns a new, unique label.'''
        self.current_label += 1
        return 'l' + str(self.current_label)

def indent(s, level):
    return '    '*level + s + '\n'

# Each of the following classes is a kind of node in the abstract syntax tree.
# indented(level) returns a string that shows the tree levels by indentation.
# code() returns a string with JVM bytecode implementing the tree fragment.
# true_code/false_code(label) jumps to label if the condition is/is not true.
# Execution of the generated code leaves the value of expressions on the stack.

class Program_AST:
    def __init__(self, program):
        self.program = program
    def __repr__(self):
        return repr(self.program)
    def indented(self, level):
        return self.program.indented(level)
    def code(self):
        program = self.program.code()
        local = symbol_table.size()
        java_scanner = symbol_table.location('Java Scanner')
        return '.class public Program\n' + \
               '.super java/lang/Object\n' + \
               '.method public <init>()V\n' + \
               'aload_0\n' + \
               'invokenonvirtual java/lang/Object/<init>()V\n' + \
               'return\n' + \
               '.end method\n' + \
               '.method public static main([Ljava/lang/String;)V\n' + \
               '.limit locals ' + str(local) + '\n' + \
               '.limit stack 1024\n' + \
               'new java/util/Scanner\n' + \
               'dup\n' + \
               'getstatic java/lang/System.in Ljava/io/InputStream;\n' + \
               'invokespecial java/util/Scanner.<init>(Ljava/io/InputStream;)V\n' + \
               'astore ' + str(java_scanner) + '\n' + \
               program + \
               'return\n' + \
               '.end method\n'

class Statements_AST:
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        result = repr(self.statements[0])
        for st in self.statements[1:]:
            result += '; ' + repr(st)
        return result
    def indented(self, level):
        result = indent('Statements', level)
        for st in self.statements:
            result += st.indented(level+1)
        return result
    def code(self):
        result = ''
        for st in self.statements:
            result += st.code()
        return result

class If_AST:
    def __init__(self, condition, then):
        self.condition = condition
        self.then = then
    def __repr__(self):
        return 'if ' + repr(self.condition) + ' then ' + \
                       repr(self.then) + ' end'
    def indented(self, level):
        return indent('If', level) + \
               self.condition.indented(level+1) + \
               self.then.indented(level+1)
    def code(self):
        l1 = label_generator.next()

        return self.condition.false_code(l1) + \
               self.then.code() + \
               l1 + ':\n'
    
class If_Else_AST:
    def __init__(self, condition, then, other):
        self.condition = condition
        self.then = then
        self.other = other
    def __repr__(self):
        return 'if ' + repr(self.condition) + ' then ' + \
                       repr(self.then) + ' else ' + repr(self.other) + ' end'
    def indented(self, level):
        return indent('If-Else', level) + \
               self.condition.indented(level+1) + \
               self.then.indented(level+1) + \
               self.other.indented(level+1)
    def code(self):
        l1 = label_generator.next()
        l2 = label_generator.next()

        return self.condition.false_code(l1) + \
               self.then.code() + \
               'goto ' + l2 + '\n' + \
               l1 + ':\n' + \
               self.other.code() + \
               l2 + ':\n'
    

class While_AST:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self):
        return 'while ' + repr(self.condition) + ' do ' + \
                          repr(self.body) + ' end'
    def indented(self, level):
        return indent('While', level) + \
               self.condition.indented(level+1) + \
               self.body.indented(level+1)
    def code(self):
        l1 = label_generator.next()
        l2 = label_generator.next()
        return l1 + ':\n' + \
               self.condition.false_code(l2) + \
               self.body.code() + \
               'goto ' + l1 + '\n' + \
               l2 + ':\n'

class Assign_AST:
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression
    def __repr__(self):
        return repr(self.identifier) + ':=' + repr(self.expression)
    def indented(self, level):
        return indent('Assign', level) + \
               self.identifier.indented(level+1) + \
               self.expression.indented(level+1)
    def code(self):
        loc = symbol_table.location(self.identifier.identifier)
        return self.expression.code() + \
               'istore ' + str(loc) + '\n'

class Write_AST:
    def __init__(self, expression):
        self.expression = expression
    def __repr__(self):
        return 'write ' + repr(self.expression)
    def indented(self, level):
        return indent('Write', level) + self.expression.indented(level+1)
    def code(self):
        return 'getstatic java/lang/System/out Ljava/io/PrintStream;\n' + \
               self.expression.code() + \
               'invokestatic java/lang/String/valueOf(I)Ljava/lang/String;\n' + \
               'invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V\n'

class Read_AST:
    def __init__(self, identifier):
        self.identifier = identifier
    def __repr__(self):
        return 'read ' + repr(self.identifier)
    def indented(self, level):
        return indent('Read', level) + self.identifier.indented(level+1)
    def code(self):
        java_scanner = symbol_table.location('Java Scanner')
        loc = symbol_table.location(self.identifier.identifier)
        return 'aload ' + str(java_scanner) + '\n' + \
               'invokevirtual java/util/Scanner.nextInt()I\n' + \
               'istore ' + str(loc) + '\n'


class Comparison_AST:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return repr(self.left) + self.op + repr(self.right)
    def indented(self, level):
        return indent(self.op, level) + \
               self.left.indented(level+1) + \
               self.right.indented(level+1)
    def true_code(self, label):
        op = { '<':'if_icmplt', '=':'if_icmpeq', '>':'if_icmpgt',
               '<=':'if_icmple', '!=':'if_icmpne', '>=':'if_icmpge' }
        return self.left.code() + \
               self.right.code() + \
               op[self.op] + ' ' + label + '\n'
    def false_code(self, label):
        # Negate each comparison because of jump to "false" label.
        op = { '<':'if_icmpge', '=':'if_icmpne', '>':'if_icmple',
               '<=':'if_icmpgt', '!=':'if_icmpeq', '>=':'if_icmplt' }
        return self.left.code() + \
               self.right.code() + \
               op[self.op] + ' ' + label + '\n'

class Boolean_Expression_AST():
    def __init__(self, left, op = None, right=None):
        self.left = left
        self.op = op
        self.right = right
    def indented(self, level):
        if self.op is None:
            return indent(self.op, level) + \
                self.left.indented(level+1)
        else:
            return indent(self.op, level) + \
                self.left.indented(level+1) + \
                self.right.indented(level+1)    
    def false_code(self, label):
        l2 = label_generator.next()
        l3 = label_generator.next()
        if self.op is not None:
            return self.left.false_code(l2) + \
                   'goto ' + l3 + '\n' + \
                   l2 + ':\n' + \
                   self.right.false_code(label) + \
                   l3 + ':\n' 
        else:
            return self.left.false_code(label)
    def true_code(self, label):
        l2 = label_generator.next()
        l3 = label_generator.next()
        if self.op is not None:
            return self.left.true_code(l2) + \
                   'goto ' + l3 + '\n' + \
                   l2 + ':\n' + \
                   self.right.true_code(label) + \
                   l3 + ':\n' 
        else:
            return self.left.true_code(label)

class Boolean_Term_AST():
    def __init__(self, left, op = None, right = None):
        self.left = left
        self.op = op
        self.right = right
    def indented(self, level):
        if self.op is None:
            return indent(self.op, level) + \
                self.left.indented(level+1)
        else:
            return indent(self.op, level) + \
                self.left.indented(level+1) + \
                self.right.indented(level+1)
        
    def false_code(self, label):
        if self.op is not None:
            return self.left.false_code(label) + \
                   self.right.false_code(label)
        else:
            return self.left.false_code(label)
        
    def true_code(self, label):
        if self.op is not None:
            return self.left.true_code(label) + \
                   self.right.true_code(label)
        else:
            return self.left.true_code(label)

class Boolean_Factor_AST():
    def __init__(self, left, right = None):
        self.left = left
        self.right = right
    def __repr__(self):
        return repr(self.left)
    def indented(self, level):
        if self.right is not None:
            return indent("NOT", level) +\
                   self.right.indented(level + 1)
        else:
            return self.left.indented(level)
        
    def false_code(self, label):
        if self.right is not None:
            return self.right.true_code(label)
        else:
            return self.left.false_code(label)
        
    def true_code(self, label):
        if self.right is not None:
            return self.right.false_code(label)
        else:
            return self.left.true_code(label) 

class Expression_AST:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return '(' + repr(self.left) + self.op + repr(self.right) + ')'
    def indented(self, level):
        return indent(self.op, level) + \
               self.left.indented(level+1) + \
               self.right.indented(level+1)
    def code(self):
        op = { '+':'iadd', '-':'isub', '*':'imul', '/':'idiv' }
        return self.left.code() + \
               self.right.code() + \
               op[self.op] + '\n'

class Number_AST:
    def __init__(self, number):
        self.number = number
    def __repr__(self):
        return self.number
    def indented(self, level):
        return indent(self.number, level)
    def code(self): # works only for short numbers
        return 'sipush ' + self.number + '\n'

class Identifier_AST:
    def __init__(self, identifier):
        self.identifier = identifier
    def __repr__(self):
        return self.identifier
    def indented(self, level):
        return indent(self.identifier, level)
    def code(self):
        loc = symbol_table.location(self.identifier)
        return 'iload ' + str(loc) + '\n'

# --------------------------------------------------------------------
#  Parser - Productions defined using the yacc library of PLY
# --------------------------------------------------------------------

precedence = (
    ('left', 'ADD', 'SUB'),
    ('left', 'MUL', 'DIV')
)

def p_program(p):
    'Program : Statements'
    p[0] = Program_AST(p[1])

def p_statements_statement(p):
    'Statements : Statement'
    p[0] = Statements_AST([p[1]])

def p_statements_statements(p):
    'Statements : Statements SEM Statement'
    sts = p[1].statements
    sts.append(p[3])
    p[0] = Statements_AST(sts)

def p_statement(p):
    '''Statement : If
                 | While
                 | Assignment
                 | Read
                 | Write'''
    p[0] = p[1]

def p_if(p):
    '''If : IF BooleanExpression THEN Statements END
          | IF BooleanExpression THEN Statements ELSE Statements END'''
    if p[5] == 'end':
        p[0] = If_AST(p[2], p[4])
    else:
        p[0] = If_Else_AST(p[2], p[4], p[6])

def p_write(p):
    'Write : WRITE Expression'
    p[0] = Write_AST(p[2])

def p_read(p):
    'Read : READ Id'
    p[0] = Read_AST(p[2])

def p_while(p):
    'While : WHILE BooleanExpression DO Statements END'
    p[0] = While_AST(p[2], p[4])

def p_assignment(p):
    'Assignment : Id BEC Expression'
    p[0] = Assign_AST(p[1], p[3])

def p_boolean_expression(p):
    '''BooleanExpression : BooleanTerm
                         | BooleanTerm OR BooleanExpression'''
    if len(p) > 2:
        p[0] = Boolean_Expression_AST(p[1], p[2], p[3])
    else:
        p[0] = p[1]

def p_boolean_term(p):
    '''BooleanTerm : BooleanFactor
                   | BooleanFactor AND BooleanTerm'''
    if len(p) > 2:
        p[0] = Boolean_Term_AST(p[1], p[2], p[3])
    else:
        p[0] = p[1]

def p_boolean_factor(p):
    '''BooleanFactor : Comparison
                     | NOT BooleanFactor'''
    if p[1] == 'not':
        p[0] = Boolean_Factor_AST(p[1], p[2])
    else:
        p[0] = p[1]

def p_comparison(p):
    'Comparison : Expression Relation Expression'
    p[0] = Comparison_AST(p[1], p[2], p[3])

def p_relation(p):
    '''Relation : EQ
                | NEQ
                | LESS
                | LEQ
                | GRTR
                | GEQ'''
    p[0] = p[1]

def p_expression_binary(p):
    '''Expression : Expression ADD Expression
                  | Expression SUB Expression
                  | Expression MUL Expression
                  | Expression DIV Expression'''
    p[0] = Expression_AST(p[1], p[2], p[3])

def p_expression_parenthesis(p):
    'Expression : LPAR Expression RPAR'
    p[0] = p[2]

def p_expression_num(p):
    'Expression : NUM'
    p[0] = Number_AST(p[1])

def p_expression_id(p):
    'Expression : Id'
    p[0] = p[1]

def p_id(p):
    'Id : ID'
    p[0] = Identifier_AST(p[1])

def p_error(p):
    print("syntax error: ", p)
    sys.exit()

scanner = lex.lex()
symbol_table = Symbol_Table()
symbol_table.location('Java Scanner') # fix a location for the Java Scanner
label_generator = Label()

# Uncomment the following to test the scanner without the parser.
# Show all tokens in the input.
#
# scanner.input(sys.stdin.read())

# for token in scanner:
#     if token.type in ['NUM', 'ID']:
#         print(token.type, token.value)
#     else:
#         print(token.type)
# sys.exit()

# Call the parser.

parser = yacc.yacc()
ast = parser.parse(sys.stdin.read(), lexer=scanner)

# Uncomment the following to test the parser without the code generator.
# Show the syntax tree with levels indicated by indentation.
#
# print(ast.indented(0), end='')
# sys.exit()

# Call the code generator.
print(ast.code(), end='')

