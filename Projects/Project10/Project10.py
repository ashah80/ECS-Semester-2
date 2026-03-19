# TODO: Parser
## go through recursively and handle each kind of statement, expression, etc. and write the corresponding XML output
## for index tracking, use some kind of token.advance() method to move through the list of tokens and keep track of the current token index
# start with compile_class, then compile necessary subroutines
# ex. class: 'class' className '{' classVarDec* subroutineDec* '}'
# classVarDec: ('static' | 'field') type varName (',' varName)* ';'

import sys
import os

# Get CLI argument for jack file
# Get CLI argument for vm file/folder

if len(sys.argv) != 2:
    print("Usage: Project10.py <input.jack or directory>", file=sys.stderr)
    sys.exit()

input_path = sys.argv[1]
jack_files = []

# If single file
if os.path.isfile(input_path) and input_path.endswith(".jack"):
    jack_files = [input_path]
    output_file = input_path.replace(".jack", ".xml")
# If directory
elif os.path.isdir(input_path):
    for file in os.listdir(input_path):
        if file.endswith(".jack"):
            jack_files.append(os.path.join(input_path, file))

    output_file = os.path.join(input_path, os.path.basename(input_path) + ".xml")
else:
    print("Invalid input path", file=sys.stderr)
    sys.exit()

keyword_list = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
symbol_list = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']

# Helper functions
# Classify the current word as keyword/identifier/integerConstant and add it to the tokens list
def endCurrentWord(currentWord, tokens):
    if currentWord:
        if currentWord in keyword_list:
            tokens.append(('keyword', currentWord))
        elif currentWord.isdigit():
            tokens.append(('integerConstant', currentWord))
        else:
            tokens.append(('identifier', currentWord))

# Block comment is the only thing that can span multiple lines, so we need to keep track of whether we're currently in a block comment or not
in_block_comment = False

# Tokenizer function that takes in the lines of the file and returns a list of tuples (lexical element, string)
def tokenize_lines(file_lines):
    global in_block_comment
    tokens = [] # list of tuples (lexical element, string)

    for line in file_lines:
        # Loop through character by character keeping track of index 
        i = 0
        in_string = False
        currentWord = ""

        while i < len(line):
            char = line[i]
            next_char = ""
            if i + 1 < len(line):
                next_char = line[i + 1]
            else:
                next_char = ""

            # Handle block comments first, since they can span multiple lines
            if in_block_comment:
                if char == '*' and next_char == '/':
                    in_block_comment = False
                    i += 2
                else:
                    i += 1
                continue

            # Handle being inside string constants
            if in_string:
                if char == '"':
                    in_string = False
                    tokens.append(('stringConstant', currentWord))
                    currentWord = ""
                else:
                    currentWord += char
                i += 1
                continue

            # Handle starting a string 
            if char == '"':
                in_string = True
                i += 1
                continue

            # Handle // comments by ignoring the rest of the line
            if char == '/' and next_char == '/':
                break

            # Handle /* comments by entering block comment mode
            if char == '/' and next_char == '*':
                in_block_comment = True
                i += 2
                continue

            # Handle symbols
            if char in symbol_list:
                # end the current word if symbol is hit
                if currentWord != "":
                    currentWord = endCurrentWord(currentWord, tokens)
                    currentWord = ""
                tokens.append(('symbol', char))
                i += 1
                continue

            # Whitespace -> end current word
            if char.isspace():
                if currentWord != "":
                    currentWord = endCurrentWord(currentWord, tokens)
                    currentWord = ""
                i += 1
                continue

            # Otherwise, add character to current word
            currentWord += char
            i += 1

        # At end of line, end current word
        if currentWord != "":
            currentWord = endCurrentWord(currentWord, tokens)
            currentWord = ""
    
    return tokens

# Parser class that takes in the list of tokens so that we can keep track of the current token index and write the corresponding XML output for each statement, expression, etc.
class Parser:
    def __init__(self, tokens, output_file):
        self.tokens = tokens
        self.i = 0
        self.output_file = output_file
        self.indent_level = 0

    # Get the current token without advancing the index
    def get_current_token(self):
        if self.i < len(self.tokens):
            return self.tokens[self.i]
        else:
            return None
    
    # Advance the index to the next token
    def advance(self):
        self.i += 1

    # Look at the next token without advancing the index
    def peek(self):
        if self.i + 1 < len(self.tokens):
            return self.tokens[self.i + 1]
        else:
            return None
        
    # Each indent level corresponds to two spaces in the output XML file
    def write_line(self, line):
        self.output_file.write("  " * self.indent_level + line + "\n")

    # Consume the current token and write the corresponding XML output line, handling special characters as needed. Then advance to the next token.
    def consume_and_print_token(self, expected_type=None, expected_value=None):
        token_type, token_value = self.get_current_token()

        if expected_type and token_type != expected_type:
            raise Exception(f"Expected token type {expected_type} but got {token_type}")
        if expected_value and token_value != expected_value:
            raise Exception(f"Expected token value {expected_value} but got {token_value}")

        # Handle special characters in XML output
        val = token_value
        if val == "<":
            val = "&lt;"
        elif val == ">":
            val = "&gt;"
        elif val == '"':
            val = "&quot;"
        elif val == '&':
            val = "&amp;"
        
        self.write_line(f"<{token_type}> {val} </{token_type}>")
        self.advance()

    def compile_class(self):
        self.write_line("<class>")
        self.indent_level += 1

        # 'class' className '{' classVarDec* subroutineDec* '}'
        self.consume_and_print_token(expected_type='keyword', expected_value='class')
        self.consume_and_print_token(expected_type='identifier') # className
        self.consume_and_print_token(expected_type='symbol', expected_value='{')

        # Handle classVarDec*
        while self.get_current_token()[1] in ['static', 'field']:
            self.compile_class_var_dec()

        # Handle subroutineDec*
        while self.get_current_token()[1] in ['constructor', 'function', 'method']:
            self.compile_subroutine_dec()

        self.consume_and_print_token(expected_type='symbol', expected_value='}') 

        self.indent_level -= 1
        self.write_line("</class>")
        

    def compile_class_var_dec(self):
        self.write_line("<classVarDec>")
        self.indent_level += 1

        # ('static' | 'field') type varName (',' varName)* ';'
        self.consume_and_print_token(expected_type='keyword') # static OR field
        self.compile_type() # type can be keyword (int, boolean, char) OR identifier (className)
        self.consume_and_print_token(expected_type='identifier') # varname

        while self.get_current_token()[1] == ',':
            self.consume_and_print_token(expected_type='symbol', expected_value=',')
            self.consume_and_print_token(expected_type='identifier') # varname
        
        self.consume_and_print_token(expected_type='symbol', expected_value=';')
        self.indent_level -= 1
        self.write_line("</classVarDec>")
    
    def compile_type(self):
        # a type can be keyword (int, boolean, char) OR identifier (className)
        if self.get_current_token()[1] in ['int', 'char', 'boolean']:
            self.consume_and_print_token(expected_type='keyword')
        else:
            self.consume_and_print_token(expected_type='identifier')

    def is_type(self):
        # check to make sure a given token is a type
        if self.get_current_token()[1] in ['int', 'char', 'boolean', 'void']:
            return True
        elif self.get_current_token()[0] == 'identifier':
            return True
        else:            
            return False
        

    def compile_subroutine_dec(self):
        self.write_line('<subroutineDec>')
        self.indent_level += 1

        # ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        self.consume_and_print_token(expected_type='keyword') # constructor OR function OR method
        if self.get_current_token()[1] == 'void':
            self.consume_and_print_token(expected_type='keyword', expected_value='void') # handle void return type
        else:
            self.compile_type() # type can be keyword (int, boolean, char) OR identifier (className)
        self.consume_and_print_token(expected_type='identifier') # subroutineName
        self.consume_and_print_token(expected_type='symbol', expected_value='(')
        self.compile_parameter_list()
        self.consume_and_print_token(expected_type='symbol', expected_value=')')
        self.compile_subroutine_body()

        self.indent_level -= 1
        self.write_line('</subroutineDec>')

    def compile_parameter_list(self):
        self.write_line('<parameterList>')
        self.indent_level += 1

        # ((type varName) (',' type varName)*)?
        if self.is_type():
            self.compile_type()
            self.consume_and_print_token(expected_type='identifier') # varName

            while self.get_current_token()[1] == ',':
                self.consume_and_print_token(expected_type='symbol', expected_value=',')
                self.compile_type()
                self.consume_and_print_token(expected_type='identifier') # varName

        self.indent_level -= 1
        self.write_line('</parameterList>')
    
    def compile_subroutine_body(self):
        self.write_line('<subroutineBody>')
        self.indent_level += 1

        # '{' varDec* statements '}'
        self.consume_and_print_token(expected_type='symbol', expected_value='{')
        while self.get_current_token()[1] == 'var':
            self.compile_var_dec()
        self.compile_statements()
        self.consume_and_print_token(expected_type='symbol', expected_value='}')

        self.indent_level -= 1
        self.write_line('</subroutineBody>')

    def compile_var_dec(self):
        self.write_line('<varDec>')
        self.indent_level += 1

        # 'var' type varName (',' varName)* ';'
        self.consume_and_print_token(expected_type='keyword', expected_value='var')
        self.compile_type()
        self.consume_and_print_token(expected_type='identifier') # varName
        while self.get_current_token()[1] == ',':
            self.consume_and_print_token(expected_type='symbol', expected_value=',')
            self.consume_and_print_token(expected_type='identifier') # varName
        self.consume_and_print_token(expected_type='symbol', expected_value=';')

        self.indent_level -= 1
        self.write_line('</varDec>')

    def compile_statements(self):
        self.write_line('<statements>')
        self.indent_level += 1

        # statements: statement*
        # statement: letStatement | ifStatement | whileStatement | doStatement | returnStatement
        while self.get_current_token()[1] in ['let', 'if', 'while', 'do', 'return']:
            if self.get_current_token()[1] == 'let':
                self.compile_let_statement()
            elif self.get_current_token()[1] == 'if':
                self.compile_if_statement()
            elif self.get_current_token()[1] == 'while':
                self.compile_while_statement()
            elif self.get_current_token()[1] == 'do':
                self.compile_do_statement()
            elif self.get_current_token()[1] == 'return':
                self.compile_return_statement()

        self.indent_level -= 1
        self.write_line('</statements>')
    
    def compile_let_statement(self):
        self.write_line('<letStatement>')
        self.indent_level += 1

        # 'let' varName ('[' expression ']')? '=' expression ';'
        self.consume_and_print_token(expected_type='keyword', expected_value='let')
        self.consume_and_print_token(expected_type='identifier') # varName
        if self.get_current_token()[1] == '[':
            self.consume_and_print_token(expected_type='symbol', expected_value='[')
            self.compile_expression()
            self.consume_and_print_token(expected_type='symbol', expected_value=']')
        self.consume_and_print_token(expected_type='symbol', expected_value='=')
        self.compile_expression()
        self.consume_and_print_token(expected_type='symbol', expected_value=';')

        self.indent_level -= 1
        self.write_line('</letStatement>')


    def compile_if_statement(self):
        self.write_line('<ifStatement>')
        self.indent_level += 1

        # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        self.consume_and_print_token(expected_type='keyword', expected_value='if')
        self.consume_and_print_token(expected_type='symbol', expected_value='(')
        self.compile_expression()
        self.consume_and_print_token(expected_type='symbol', expected_value=')')
        self.consume_and_print_token(expected_type='symbol', expected_value='{')
        self.compile_statements()
        self.consume_and_print_token(expected_type='symbol', expected_value='}')
        if self.get_current_token()[1] == 'else':
            self.consume_and_print_token(expected_type='keyword', expected_value='else')
            self.consume_and_print_token(expected_type='symbol', expected_value='{')
            self.compile_statements()
            self.consume_and_print_token(expected_type='symbol', expected_value='}')

        self.indent_level -= 1
        self.write_line('</ifStatement>')

    def compile_while_statement(self):
        self.write_line('<whileStatement>')
        self.indent_level += 1

        # 'while' '(' expression ')' '{' statements '}'
        self.consume_and_print_token(expected_type='keyword', expected_value='while')
        self.consume_and_print_token(expected_type='symbol', expected_value='(')
        self.compile_expression()
        self.consume_and_print_token(expected_type='symbol', expected_value=')')
        self.consume_and_print_token(expected_type='symbol', expected_value='{')
        self.compile_statements()
        self.consume_and_print_token(expected_type='symbol', expected_value='}')

        self.indent_level -= 1
        self.write_line('</whileStatement>')

    def compile_do_statement(self):
        self.write_line('<doStatement>')
        self.indent_level += 1

        # 'do' subroutineCall ';'
        self.consume_and_print_token(expected_type='keyword', expected_value='do')
        self.compile_subroutine_call()
        self.consume_and_print_token(expected_type='symbol', expected_value=';')

        self.indent_level -= 1
        self.write_line('</doStatement>')

    def compile_return_statement(self):
        self.write_line('<returnStatement>')
        self.indent_level += 1

        # 'return' expression? ';'
        self.consume_and_print_token(expected_type='keyword', expected_value='return')
        if self.get_current_token()[1] != ';':
            self.compile_expression()
        self.consume_and_print_token(expected_type='symbol', expected_value=';')

        self.indent_level -= 1
        self.write_line('</returnStatement>')

    def compile_expression(self):
        self.write_line('<expression>')
        self.indent_level += 1

        # term (op term)*
        self.compile_term()
        while self.get_current_token()[1] in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            self.consume_and_print_token(expected_type='symbol') # op
            self.compile_term()

        self.indent_level -= 1
        self.write_line('</expression>')

    def compile_term(self):
        self.write_line('<term>')
        self.indent_level += 1

        # integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
        if self.get_current_token()[0] == 'integerConstant': # integerConstant
            self.consume_and_print_token(expected_type='integerConstant')
        elif self.get_current_token()[0] == 'stringConstant': # stringConstant
            self.consume_and_print_token(expected_type='stringConstant')
        elif self.get_current_token()[1] in ['true', 'false', 'null', 'this']: # keywordConstant
            self.consume_and_print_token(expected_type='keyword')
        elif self.get_current_token()[1] == '(': # expression
            self.consume_and_print_token(expected_type='symbol', expected_value='(')
            self.compile_expression()
            self.consume_and_print_token(expected_type='symbol', expected_value=')')
        elif self.get_current_token()[1] in ['-', '~']: # unaryOp
            self.consume_and_print_token(expected_type='symbol')
            self.compile_term()
        else:
            # Differentiate between varName and subRoutineCall by looking ahead for a '('
            if self.peek()[1] in ['(', '.']: # subroutineCall 
                self.compile_subroutine_call()
            else: # varName, need to differentiate between varName and varName '[' expression ']'
                self.consume_and_print_token(expected_type='identifier') # varName
                if self.get_current_token()[1] == '[':
                    self.consume_and_print_token(expected_type='symbol', expected_value='[')
                    self.compile_expression()
                    self.consume_and_print_token(expected_type='symbol', expected_value=']')

        self.indent_level -= 1
        self.write_line('</term>')

    def compile_subroutine_call(self):
        # not wrapped in a tag for some reason?

        # subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
        self.consume_and_print_token(expected_type='identifier') # subroutineName OR className OR varName
        if self.get_current_token()[1] == '.': # period is only preceded by className or varName, not subroutineName
            self.consume_and_print_token(expected_type='symbol', expected_value='.')
            self.consume_and_print_token(expected_type='identifier') # subroutineName
        # compile the '(' expressionList ')' part no matter what
        self.consume_and_print_token(expected_type='symbol', expected_value='(')
        self.compile_expression_list()
        self.consume_and_print_token(expected_type='symbol', expected_value=')')

    def compile_expression_list(self):
        self.write_line('<expressionList>')
        self.indent_level += 1

        # (expression (',' expression)*)?
        if self.get_current_token()[1] != ')': # if the next token is a ')' then the expression list is empty (because the expression list is always followed by a ')')
            self.compile_expression()
            # repeat until no more expressions are left, which is indicated by no more commas
            while self.get_current_token()[1] == ',':
                self.consume_and_print_token(expected_type='symbol', expected_value=',')
                self.compile_expression()

        self.indent_level -= 1
        self.write_line('</expressionList>')

for jack_file in jack_files:
    jack_basename = os.path.basename(jack_file).replace(".jack", "")
    output_path = os.path.join(os.path.dirname(jack_file), jack_basename + "TMINE.xml")
    file_lines = []
    all_tokens = []
    with open(jack_file, 'r') as file:
        for line in file:
            file_lines.append(line)

    all_tokens = tokenize_lines(file_lines)

    # Output in xml file
    with open(output_path, 'w') as xml_file:
        xml_file.write('<tokens>\n')
        for token in all_tokens:
            if token[1] == "<":
                xml_file.write(f'<{token[0]}> &lt; </{token[0]}>\n')
            elif token[1] == ">":
                xml_file.write(f'<{token[0]}> &gt; </{token[0]}>\n')
            elif token[1] == '"':
                xml_file.write(f'<{token[0]}> &quot; </{token[0]}>\n')
            elif token[1] == '&':
                xml_file.write(f'<{token[0]}> &amp; </{token[0]}>\n')
            else:
                xml_file.write(f'<{token[0]}> {token[1]} </{token[0]}>\n')
        xml_file.write('</tokens>\n')