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
        if self.get_current_token()[1] in ['int', 'char', 'boolean', 'void']:
            self.consume_and_print_token(expected_type='keyword')
        else:
            self.consume_and_print_token(expected_type='identifier')

    def compile_subroutine_dec(self):
        self.write_line("<subroutineDec>")
        self.indent_level += 1

        # ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        self.consume_and_print_token(expected_type='keyword') # constructor OR function OR method
        self.compile_type() # void OR type, this function handles both
        self.consume_and_print_token(expected_type='identifier') # subroutineName
        self.consume_and_print_token(expected_type='symbol', expected_value='(')
        self.compile_parameter_list()
        self.consume_and_print_token(expected_type='symbol', expected_value=')')
        self.compile_subroutine_body()

        self.indent_level -= 1
        self.write_line("</subroutineDec>")


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