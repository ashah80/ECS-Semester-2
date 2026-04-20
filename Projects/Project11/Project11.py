import sys
import os

# Get CLI argument for jack file/folder
if len(sys.argv) != 2:
    print("Usage: Project10.py <input.jack or directory>", file=sys.stderr)
    sys.exit()

input_path = sys.argv[1]
jack_files = []

# If single file
if os.path.isfile(input_path) and input_path.endswith(".jack"):
    jack_files = [input_path]
    output_file = input_path.replace(".jack", ".vm")
# If directory
elif os.path.isdir(input_path):
    for file in os.listdir(input_path):
        if file.endswith(".jack"):
            jack_files.append(os.path.join(input_path, file))

    output_file = os.path.join(input_path, os.path.basename(input_path) + ".vm")
else:
    print("Invalid input path", file=sys.stderr)
    sys.exit()

keyword_list = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
symbol_list = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']

class Tokenizer:
    def __init__(self, file_path, output_file=None):
        self.file_path = file_path
        self.output_file = output_file
        self.tokens = [] # list of tuples (lexical element, string)
        # Block comment is the only thing that can span multiple lines, so we need to keep track of whether we're currently in a block comment or not
        self.in_block_comment = False

    def print_tokens_to_xml(self, all_tokens, output_file):
        with open(output_file, 'w') as xml_file:
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


        
    def tokenize(self):
        """
        Main function for tokenizer: Read in the file, tokenize it, and return the list of tokens as tuples (lexical element, string)
        """
        with open(self.file_path, 'r') as file:
            file_lines = file.readlines()
            self.tokens = self.tokenize_lines(file_lines)
        return self.tokens
    
    def endCurrentWord(self, currentWord, tokens):
        """
        Helper function for tokenizer: Classify the current word as keyword/identifier/integerConstant and add it to the tokens list
        """
        if currentWord:
            if currentWord in keyword_list:
                tokens.append(('keyword', currentWord))
            elif currentWord.isdigit():
                tokens.append(('integerConstant', currentWord))
            else:
                tokens.append(('identifier', currentWord))
        currentWord = ""
        return currentWord

    def tokenize_lines(self, file_lines):
        """
        Tokenizer function that takes in the lines of the file and returns a list of tuples (lexical element, string)
        """
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
                if self.in_block_comment:
                    if char == '*' and next_char == '/':
                        self.in_block_comment = False
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
                    self.in_block_comment = True
                    i += 2
                    continue

                # Handle symbols
                if char in symbol_list:
                    # end the current word if symbol is hit
                    if currentWord != "":
                        currentWord = self.endCurrentWord(currentWord, tokens)
                        currentWord = ""
                    tokens.append(('symbol', char))
                    i += 1
                    continue

                # Whitespace -> end current word
                if char.isspace():
                    if currentWord != "":
                        currentWord = self.endCurrentWord(currentWord, tokens)
                        currentWord = ""
                    i += 1
                    continue

                # Otherwise, add character to current word
                currentWord += char
                i += 1

            # At end of line, end current word
            if currentWord != "":
                currentWord = self.endCurrentWord(currentWord, tokens)
                currentWord = ""
        
        return tokens    
    



class Parser:
    """
    Parser class that takes in the list of tokens so that we can keep track of the current token index and write the corresponding XML output for each statement, expression, etc.
    """
    def __init__(self, tokens, vm_file):
        self.tokens = tokens
        self.i = 0
        self.vm_file = vm_file
        self.indent_level = 0
        self.class_table = SymbolTable() # symbol table for class-level variables
        self.subroutine_table = SymbolTable() # symbol table for subroutine-level variables
        self.class_name = "" # for "function ClassName.subroutineName nLocals" 
        self.nLocals = 0

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
        
    # TODO: Delete all print statements, then delete this function, bc im no longer printing XML
    def write_line(self, line):
        # self.vm_file.write("  " * self.indent_level + line + "\n")
        pass

    def consume_token(self, expected_type=None, expected_value=None):
        """
        Consume the current token and write the corresponding XML output line (after checking that the type and value match, if provided), handling special characters as needed. Then advance to the next token.
        """
        token_type, token_value = self.get_current_token()

        if expected_type and token_type != expected_type:
            raise Exception(f"Expected token type {expected_type} but got {token_type}")
        if expected_value and token_value != expected_value:
            raise Exception(f"Expected token value {expected_value} but got {token_value}")
        
        self.advance()
        return token_value

    def compile_class(self):
        # 'class' className '{' classVarDec* subroutineDec* '}'
        self.consume_token(expected_type='keyword', expected_value='class')
        self.class_name = self.get_current_token()[1] # save class name for later use
        self.consume_token(expected_type='identifier') # className
        self.consume_token(expected_type='symbol', expected_value='{')

        # Handle classVarDec*
        while self.get_current_token()[1] in ['static', 'field']:
            self.compile_class_var_dec()

        # Handle subroutineDec*
        while self.get_current_token()[1] in ['constructor', 'function', 'method']:
            self.compile_subroutine_dec()

        self.consume_token(expected_type='symbol', expected_value='}') 

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
        if self.get_current_token()[1] in ['int', 'char', 'boolean']:
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
    
class SymbolTable:
    """
    Symbol table class that keeps track of the variables in the current scope (class-level and subroutine-level) and their corresponding type, kind, and index. Used to generate the correct VM code for variable access. 
    """
    def __init__(self):
        self.table = {} # dictionary mapping variable names to a tuple of (type , kind, index)
        self.counters = {'static': 0, 'field': 0, 'arg': 0, 'var': 0}
    
    # Wipe the table and reset the counters, to be used when starting to compile a new subroutine (since subroutine-level variables go out of scope and we need to start fresh for the next subroutine)
    def reset(self):
        self.table = {}
        self.counters = {'static': 0, 'field': 0, 'arg': 0, 'var': 0}

    # Define a new variable and assign it an index based on how many variables of the same kind have already been defined.
    def define(self, name, var_type, kind):
        index = self.counters[kind]
        self.table[name] = (var_type, kind, index)
        self.counters[kind] += 1

    # Return the information for a variable if it exists in the table, otherwise return None
    def get_var(self, name):
        return self.table.get(name, None)


# VM Helper Functions
def write_vm_push(file, segment, index):
    file.write(f"push {segment} {index}\n")

def write_vm_pop(file, segment, index):
    file.write(f"pop {segment} {index}\n")

def write_vm_arithmetic(file, command):
    file.write(f"{command}\n")

def write_vm_label(file, label):
    file.write(f"label {label}\n")

def write_vm_goto(file, label):
    file.write(f"goto {label}\n")

def write_vm_if(file, label):
    file.write(f"if-goto {label}\n")

def write_vm_call(file, name, n_args):
    file.write(f"call {name} {n_args}\n")

def write_vm_function(file, name, n_locals):
    file.write(f"function {name} {n_locals}\n")

def write_vm_return(file):
    file.write("return\n")

for jack_file in jack_files:
    jack_basename = os.path.basename(jack_file).replace(".jack", "")
    tokenizer_output_path = os.path.join(os.path.dirname(jack_file), jack_basename + "T.xml")
    parser_output_path = os.path.join(os.path.dirname(jack_file), jack_basename + ".vm")

    file_lines = []
    all_tokens = []
    with open(jack_file, 'r') as file:
        for line in file:
            file_lines.append(line)

    # Get tokens
    tokenizer = Tokenizer(jack_file)
    all_tokens = tokenizer.tokenize()
    tokenizer.print_tokens_to_xml(all_tokens, tokenizer_output_path)

    # Write parsed output to VM file
    with open(parser_output_path, 'w') as vm_file:
        parser = Parser(all_tokens, vm_file)
        parser.compile_class()