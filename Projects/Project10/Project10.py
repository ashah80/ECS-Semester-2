# TODO: Tokenizer
## Go through the jack file character by character, build a list of tuples (lexical element, string)
## Ignore comments and spaces

# TODO: Parser
## go through recursively and handle each kind of statement, expression, etc. and write the corresponding XML output
## for index tracking, use some kind of token.advance() method to move through the list of tokens and keep track of the current token index
# start with compile_class, then compile necessary subroutines
# ex. class: 'class' className '{' classVarDec* subroutineDec* '}'
# classVarDec: ('static' | 'field') type varName (',' varName)* ';'

import sys

# Get CLI argument for jack file
jack_file = ""
jack_basename = ""
if len(sys.argv) == 2 and sys.argv[1].endswith('.jack'):
    jack_file = sys.argv[1]
    jack_basename = jack_file.replace('.jack', '')
else:
    print("Usage Error: Project10.py <input_file.jack>", file=sys.stderr)
    sys.exit()

# Read from input file character by character, build a list of tuples (lexical element, string)
instructions = []
with open(jack_file, 'r') as file:
    for line in file:
        line = line.strip()
    