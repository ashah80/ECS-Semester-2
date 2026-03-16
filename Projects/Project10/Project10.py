# TODO: Parser
## go through recursively and handle each kind of statement, expression, etc. and write the corresponding XML output
## for index tracking, use some kind of token.advance() method to move through the list of tokens and keep track of the current token index
# start with compile_class, then compile necessary subroutines
# ex. class: 'class' className '{' classVarDec* subroutineDec* '}'
# classVarDec: ('static' | 'field') type varName (',' varName)* ';'

# TODO: Take in multiple jack files and output multiple xml files

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