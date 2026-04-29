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
        self.label_count = 0 # for generating unique labels in if and while statements

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
        
    def lookup_variable(self, name):
        # Look up a variable in the subroutine-level symbol table first, then the class-level symbol table, and return its information (type, kind, index) if found, otherwise return None
        var_info = self.subroutine_table.get_var(name)
        if var_info is not None:
            return var_info
        else:
            return self.class_table.get_var(name)
        
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
        # ('static' | 'field') type varName (',' varName)* ';'
        kind = self.consume_token(expected_type='keyword') # static OR field
        var_type = self.compile_type() # type can be keyword (int, boolean, char) OR identifier (className)
        var_name = self.consume_token(expected_type='identifier') # varname
        self.class_table.define(var_name, var_type, kind) # add class-level variable to symbol table

        while self.get_current_token()[1] == ',':
            self.consume_token(expected_type='symbol', expected_value=',')
            var_name = self.consume_token(expected_type='identifier') # varname
            self.class_table.define(var_name, var_type, kind)
        
        self.consume_token(expected_type='symbol', expected_value=';')
    
    def compile_type(self):
        # a type can be keyword (int, boolean, char) OR identifier (className)
        token = self.get_current_token()
        if self.get_current_token()[1] in ['int', 'char', 'boolean']:
            self.consume_token(expected_type='keyword')
        else:
            self.consume_token(expected_type='identifier')
        return token[1]

    def is_type(self):
        # check to make sure a given token is a type
        if self.get_current_token()[1] in ['int', 'char', 'boolean']:
            return True
        elif self.get_current_token()[0] == 'identifier':
            return True
        else:            
            return False
        
    def compile_subroutine_dec(self):
        # ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        self.subroutine_table.reset() # reset for each new subroutine 

        subroutine_type = self.consume_token(expected_type='keyword') # constructor OR function OR method
        if self.get_current_token()[1] == 'void':
            self.consume_token(expected_type='keyword', expected_value='void') # handle void return type
        else:
            self.compile_type() # type can be keyword (int, boolean, char) OR identifier (className)

        subroutine_name = self.consume_token(expected_type='identifier') # subroutineName
        # Methods get "this" as the first argument 
        if subroutine_type == 'method':
            self.subroutine_table.define('this', self.class_name, 'argument') # add "this" to symbol table as the first argument

        self.consume_token(expected_type='symbol', expected_value='(')
        self.compile_parameter_list()
        self.consume_token(expected_type='symbol', expected_value=')')
        self.compile_subroutine_body(subroutine_name, subroutine_type)

    def compile_parameter_list(self):
        # ((type varName) (',' type varName)*)?

        if self.is_type():
            var_type = self.compile_type()
            var_name = self.consume_token(expected_type='identifier') # varName
            self.subroutine_table.define(var_name, var_type, 'argument')

            while self.get_current_token()[1] == ',':
                self.consume_token(expected_type='symbol', expected_value=',')
                var_type = self.compile_type()
                var_name = self.consume_token(expected_type='identifier') # varName
                self.subroutine_table.define(var_name, var_type, 'argument')
    
    def compile_subroutine_body(self, subroutine_name, subroutine_type):
        # '{' varDec* statements '}'
        self.consume_token(expected_type='symbol', expected_value='{')

        while self.get_current_token()[1] == 'var':
            self.compile_var_dec()

        # Now we know how many locals there are so we can write the function declaration in VM ("function ClassName.subroutineName nLocals")
        n_locals = self.subroutine_table.counters['local']
        write_vm_function(self.vm_file, f"{self.class_name}.{subroutine_name}", n_locals)

        # Compiling constructors/methods preamble
        if subroutine_type == 'constructor':
            # For constructors, we need to allocate memory for the object and set "this" to point to that memory
            n_fields = self.class_table.counters['field']
            write_vm_push(self.vm_file, 'constant', n_fields) # push the number of fields (the size of the object)
            write_vm_call(self.vm_file, 'Memory.alloc', 1) # call Memory.alloc to allocate that much memory, which leaves the base address of the allocated memory on the stack
            write_vm_pop(self.vm_file, 'pointer', 0) # pop that base address into pointer 0, which sets "this" to point to the allocated memory

        elif subroutine_type == 'method':
            # For methods, we need to set "this" to point to the object that the method is being called on, which is passed as the first argument (argument 0)
            write_vm_push(self.vm_file, 'argument', 0) # push argument 0, which is the base address of the object that the method is being called on
            write_vm_pop(self.vm_file, 'pointer', 0) # pop that base address into pointer 0, which sets "this" to point to the object

        self.compile_statements()
        self.consume_token(expected_type='symbol', expected_value='}')

    def compile_var_dec(self):
        # 'var' type varName (',' varName)* ';'
        self.consume_token(expected_type='keyword', expected_value='var')
        var_type = self.compile_type()
        var_name = self.consume_token(expected_type='identifier') # varName
        self.subroutine_table.define(var_name, var_type, 'local') # add subroutine-level variable to symbol table

        while self.get_current_token()[1] == ',':
            self.consume_token(expected_type='symbol', expected_value=',')
            var_name = self.consume_token(expected_type='identifier') # varName
            self.subroutine_table.define(var_name, var_type, 'local')
        self.consume_token(expected_type='symbol', expected_value=';')

        self.indent_level -= 1
        self.write_line('</varDec>')

    # TODO: Fix
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
        # 'let' varName ('[' expression ']')? '=' expression ';'

        self.consume_and_print_token(expected_type='keyword', expected_value='let')
        var_name = self.consume_and_print_token(expected_type='identifier') # varName
        var_info = self.lookup_variable(var_name)

        # If array
        if self.get_current_token()[1] == '[':
            # Push base address + index to get target address
            write_vm_push(self.vm_file, var_info[1], var_info[2])
            self.consume_token(expected_type='symbol', expected_value='[')
            self.compile_expression() # pushes index
            write_vm_arithmetic(self.vm_file, 'add')
            self.consume_token(expected_type='symbol', expected_value=']')
            self.consume_token(expected_type='symbol', expected_value='=')
            self.compile_expression() # pushes value to assign

            write_vm_pop(self.vm_file, 'temp', 0) # save value to assign
            write_vm_pop(self.vm_file, 'pointer', 1) # pop target address into pointer 1 (means "that" now points to the target array element)
            write_vm_push(self.vm_file, 'temp', 0) # push value to assign (again)
            write_vm_pop(self.vm_file, 'that', 0) # pop value to assign into that 0, which assigns it to the target array element

        # If regular, pop the value of the expression into the variable based on its kind and index
        else: 
            self.consume_token(expected_type='symbol', expected_value='=')
            self.compile_expression()
            write_vm_pop(self.vm_file, var_info[1], var_info[2]) 
            
        self.consume_token(expected_type='symbol', expected_value=';')

    def compile_if_statement(self):
        # 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        current_label_num = self.label_count
        self.label_count += 1

        self.consume_token(expected_type='keyword', expected_value='if')
        self.consume_token(expected_type='symbol', expected_value='(')
        
        self.compile_expression() # pushes condition
        write_vm_arithmetic(self.vm_file, 'not') # negate condition
        false_label = f"IF_FALSE_L{current_label_num}" # unique label for the false
        end_label = f"IF_END_L{current_label_num}"
        write_vm_if(self.vm_file, false_label) # if NOT condition, jump to false label

        self.consume_token(expected_type='symbol', expected_value=')')
        self.consume_token(expected_type='symbol', expected_value='{')
        self.compile_statements() # true branch
        self.consume_token(expected_type='symbol', expected_value='}')

        if self.get_current_token()[1] == 'else':
            write_vm_goto(self.vm_file, end_label) # jump to end label after true branch
            write_vm_label(self.vm_file, false_label) # if condition is false we jump to this point
            
            self.consume_token(expected_type='keyword', expected_value='else')
            self.consume_token(expected_type='symbol', expected_value='{')
            self.compile_statements() # false branch
            self.consume_token(expected_type='symbol', expected_value='}')
            
            write_vm_label(self.vm_file, end_label) # write the end label
        else:
            write_vm_label(self.vm_file, false_label) # if no else condition, just skip the branch if condition is false

    # TODO: Fix
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
        # 'do' subroutineCall ';'

        self.consume_token(expected_type='keyword', expected_value='do')
        self.compile_subroutine_call()
        self.consume_token(expected_type='symbol', expected_value=';')

        # remove return value from stack
        write_vm_pop(self.vm_file, 'temp', 0)

    def compile_return_statement(self):
        # 'return' expression? ';'
        
        self.consume_token(expected_type='keyword', expected_value='return')
        if self.get_current_token()[1] != ';':
            self.compile_expression()
        else:
            write_vm_push(self.vm_file, 'constant', 0) # "push constant 0" for void functions

        self.consume_token(expected_type='symbol', expected_value=';')
        write_vm_return(self.vm_file)

    def compile_expression(self):
        # term (op term)*

        self.compile_term()
        while self.get_current_token()[1] in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            op = self.consume_token(expected_type='symbol') # op
            self.compile_term()

            # Print the operator after the second term (because postfix)
            if op == '+': write_vm_arithmetic(self.vm_file, 'add')
            elif op == '-': write_vm_arithmetic(self.vm_file, 'sub')
            elif op == '*': write_vm_call(self.vm_file, 'Math.multiply', 2)
            elif op == '/': write_vm_call(self.vm_file, 'Math.divide', 2)
            elif op == '&': write_vm_arithmetic(self.vm_file, 'and')
            elif op == '|': write_vm_arithmetic(self.vm_file, 'or')
            elif op == '<': write_vm_arithmetic(self.vm_file, 'lt')
            elif op == '>': write_vm_arithmetic(self.vm_file, 'gt')
            elif op == '=': write_vm_arithmetic(self.vm_file, 'eq')

    def compile_term(self):
        # integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term

        if self.get_current_token()[0] == 'integerConstant': # integerConstant
            integer_value = self.consume_token(expected_type='integerConstant')
            write_vm_push(self.vm_file, 'constant', integer_value)

        elif self.get_current_token()[0] == 'stringConstant': # stringConstant
            string_value = self.consume_token(expected_type='stringConstant')
            write_vm_push(self.vm_file, 'constant', len(string_value))
            write_vm_call(self.vm_file, 'String.new', 1)
            for char in string_value:
                write_vm_push(self.vm_file, 'constant', ord(char))
                write_vm_call(self.vm_file, 'String.appendChar', 2) # 2 arguments are the string and char to append 

        elif self.get_current_token()[1] in ['true', 'false', 'null', 'this']: # keywordConstant
            keyword_constant_value = self.consume_token(expected_type='keyword')
            if keyword_constant_value == 'true':
                write_vm_push(self.vm_file, 'constant', 1)
                write_vm_arithmetic(self.vm_file, 'neg') # true is represented as -1 in VM
            elif keyword_constant_value in ['false', 'null']:
                write_vm_push(self.vm_file, 'constant', 0) # false and null are both represented as 0 in VM
            elif keyword_constant_value == 'this':
                write_vm_push(self.vm_file, 'pointer', 0) # "this" is represented as pointer 0 in VM

        elif self.get_current_token()[1] == '(': # expression
            self.consume_token(expected_type='symbol', expected_value='(')
            self.compile_expression()
            self.consume_token(expected_type='symbol', expected_value=')')

        elif self.get_current_token()[1] in ['-', '~']: # unaryOp
            op = self.consume_token(expected_type='symbol')
            self.compile_term()
            if op == '-': write_vm_arithmetic(self.vm_file, 'neg')
            elif op == '~': write_vm_arithmetic(self.vm_file, 'not')

        else:
            # Differentiate between varName and subRoutineCall by looking ahead for a '('
            if self.peek()[1] in ['(', '.']: # subroutineCall 
                self.compile_subroutine_call()
            else: # varName, need to differentiate between varName and varName '[' expression ']'
                var_name = self.consume_token(expected_type='identifier') # varName
                # handle reading from an array
                if self.get_current_token()[1] == '[':
                    var_info = self.lookup_variable(var_name)
                    write_vm_push(self.vm_file, var_info[1], var_info[2]) # push the base address of the array onto the stack
                    self.consume_token(expected_type='symbol', expected_value='[')
                    self.compile_expression() # pushes the index onto the stack
                    write_vm_arithmetic(self.vm_file, 'add') # add the base address and index
                    write_vm_pop(self.vm_file, 'pointer', 1) # pop the resulting address into pointer 1 (that means "that" now points to the target array element)
                    write_vm_push(self.vm_file, 'that', 0) # push the value at that address onto the stack
                    self.consume_token(expected_type='symbol', expected_value=']')
                # plain varName
                else: 
                    var_info = self.lookup_variable(var_name)
                    write_vm_push(self.vm_file, var_info[1], var_info[2]) # push the variable onto the stack based on its kind and index in the symbol table
    
    def compile_subroutine_call(self):
        # subroutineName '(' expressionList ')' | (className | varName) '.' subroutineName '(' expressionList ')'
        name = self.consume_token(expected_type='identifier') # subroutineName OR className OR varName

        if self.get_current_token()[1] == '.': # period is only preceded by className or varName, not subroutineName
            self.consume_token(expected_type='symbol', expected_value='.')
            subroutine_name = self.consume_token(expected_type='identifier') # subroutineName
            var_info = self.lookup_variable(name)
            if var_info is not None: # this is a variable
                write_vm_push(self.vm_file, var_info[1], var_info[2]) # push the variable (the object that the method is being called on) onto the stack as the first argument for the method call
                full_name = f"{var_info[0]}.{subroutine_name}" # className.subroutine
                n_args = 1 # the object that the method is being called on is the first argument
            else: # this is a className
                full_name = f"{name}.{subroutine_name}" # className.subroutine
                n_args = 0

        else: # no period means it's a subroutineName with an implicit class (the current class), so we need to add the class name in front of it for the VM function call
            full_name = f"{self.class_name}.{name}"
            n_args = 0

        # compile the '(' expressionList ')' part no matter what
        self.consume_and_print_token(expected_type='symbol', expected_value='(')
        num_expressions = self.compile_expression_list()
        self.consume_and_print_token(expected_type='symbol', expected_value=')')

        # Call the subroutine with the number of arguments
        n_args += num_expressions
        write_vm_call(self.vm_file, full_name, n_args)


    def compile_expression_list(self):
        # (expression (',' expression)*)?
        num_expressions = 0

        if self.get_current_token()[1] != ')': # if the next token is a ')' then the expression list is empty (because the expression list is always followed by a ')')
            self.compile_expression()
            num_expressions += 1

            # repeat until no more expressions are left, which is indicated by no more commas
            while self.get_current_token()[1] == ',':
                self.consume_and_print_token(expected_type='symbol', expected_value=',')
                self.compile_expression()
                num_expressions += 1

        return num_expressions

class SymbolTable:
    """
    Symbol table class that keeps track of the variables in the current scope (class-level and subroutine-level) and their corresponding type, kind, and index. Used to generate the correct VM code for variable access. 
    """
    def __init__(self):
        self.table = {} # dictionary mapping variable names to a tuple of (type , kind, index)
        self.counters = {'static': 0, 'field': 0, 'argument': 0, 'local': 0}
    
    # Wipe the table and reset the counters, to be used when starting to compile a new subroutine (since subroutine-level variables go out of scope and we need to start fresh for the next subroutine)
    def reset(self):
        self.table = {}
        self.counters = {'static': 0, 'field': 0, 'argument': 0, 'local': 0}

    # Define a new variable and assign it an index based on how many variables of the same kind have already been defined.
    def define(self, name, var_type, kind):
        index = self.counters[kind]
        if kind == 'field':
            kind = 'this' # field variables are accessed with the "this" segment in VM (everything else is reference by its regular name)
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