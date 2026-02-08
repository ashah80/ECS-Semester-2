import sys

# Get CLI argument for vm file 
vm_file = ""
if len(sys.argv) == 2 and sys.argv[1].endswith('.vm'):
    vm_file = sys.argv[1]
else:
    print("Usage Error: Assignment1.py <input_file.vm>", file=sys.stderr)
    sys.exit()

# Read from input file, avoid whitespace/comments, store in a list
instructions = []
with open(vm_file, 'r') as file:
    for line in file:
        line = line.strip()
        if '//' in line:
            line = line[:line.index('//')].strip()
        if line and not line.startswith('//'):
            instructions.append(line)
print(instructions)

# SP decrementer helper function
def decrement_pointer():
    """
    Decrements the stack pointer by 1.
    """
    return ["@SP", "M=M-1"]

def increment_pointer():
    """
    Increments the stack pointer by 1
    """
    return ["@SP", "M=M+1"]


# Helper functions for pushing and popping from the stack

def push_constant(value):
    """
    Pushes D onto stack.
    This function takes in a value, loads it into the D register, goes to the address of the stack pointer, stores the value in that memory address, increments stack pointer.
    """
    return [f"@{value}", "D=A", "@SP", "A=M", "M=D"] + increment_pointer()

def pop_from_stack():
    """
    Pops the top of the stack and stores in D.
    This function decrements the stack pointer, then stores the value at that memory address in the D register.
    """
    return decrement_pointer() + ["A=M", "D=M"]
    
# Helper functions for single-argument commands
def handle_neg():
    """
    Flips the sign of the top value on the stack.
    Stores the decremented value of the stack pointer in the A register, then flips the sign of that value.
    """
    return ["@SP", "A=M-1", "M=-M"]

def handle_not():
    """
    Performs a bitwise negation of the top value on the stack.
    Similar implementation to handle_neg(), but with a not(!) instead of a negative(-)
    """
    return ["@SP", "A=M-1", "M=!M"]

# Helper functions for arithmetic commands
def handle_add():
    """
    Adds the top two values on the stack.
    Pops a value from the stack, puts it in the D register, adds it to the 2nd-top value on the stack.
    """
    return pop_from_stack() + ["@SP", "A=M-1", "M=D+M"]

def handle_sub():
    """
    Adds the top two values on the stack.
    Pops a value from the stack (which is stored in the D register) subtracts it from the next value on the stack.
    """
    return pop_from_stack() + ["@SP", "A=M-1", "M=M-D"]

def handle_and():
    """
    Bitwise "and" of the top two values on the stack 
    Pops a value from the stack (which is stored in the D register), "ands" it with the next value on the stack.
    """
    return pop_from_stack() + ["@SP", "A=M-1", "M=D&M"]

def handle_or():
    """
    Bitwise "or" of the top two values on the stack 
    Pops a value from the stack (which is stored in the D register), "ors" it with the next value on the stack.
    """
    return pop_from_stack() + ["@SP", "A=M-1", "M=D|M"]


# Helper functions for local, argument, this, that segments
segment_pointers = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT"
}

def push_from_segment(segment, index):
    """
    Pushes a value from a segment onto the stack.
    This function takes in a segment and index, calculates the address of that segment and index, stores the value at that memory address in the D register, then pushes that value onto the stack.
    """
    
    return [f"@{index}", "D=A", f"@{segment_pointers[segment]}", "A=D+M", "D=M", "@SP", "A=M", "M=D"] + increment_pointer()

def pop_from_segment(segment, index):
    """
    Pops a value from the stack and stores it in a segment.
    This function takes in a segment and index, calculates the address of that segment and index, pops a value from the stack (which is stored in the D register), then stores that value at the calculated memory address.
    """
    
    return [f"@{index}", "D=A", f"@{segment_pointers[segment]}", "D=D+M", "@R13", "M=D"] + pop_from_stack() + ["@R13", "A=M", "M=D"]

label_counter = 0
# Helper functions for gt, lt, eq commands
def generate_unique_label(condition):
    """
    Generates a unique label for conditional commands.
    This function takes in a condition ("TRUE", "END") and returns a unique label string based on that condition and a counter.
    """
    global label_counter
    label = f"{condition}_{label_counter}"
    label_counter += 1
    return label

def handle_comparison(command):
    """
    Handles gt, lt, eq commands.
    This function takes in a command ("gt", "lt", "eq"), pops two values from the stack, compares them based on the command, and pushes -1 (true) or 0 (false) onto the stack based on the result of the comparison.
    """

    # Generate labels for true/false/end conditions
    true_label = generate_unique_label("TRUE")
    end_label = generate_unique_label("END")

    hack_asm = []

    # Pop from top of stack into D
    hack_asm += pop_from_stack()

    # Load next value on stack into A, then compute x - y and store in D
    hack_asm += ["@SP", "A=M-1", "D=M-D"]

    # Jump to true_label if condition is met
    if command == "eq":
        hack_asm += [f"@{true_label}", "D;JEQ"]
    elif command == "gt":
        hack_asm += [f"@{true_label}", "D;JGT"]
    elif command == "lt":
        hack_asm += [f"@{true_label}", "D;JLT"]

    # If condition is not met, push 0 (false) onto stack and jump to end_label
    hack_asm += ["@SP", "A=M-1", "M=0", f"@{end_label}", "0;JMP"]

    # If condition is met, push -1 (true) onto stack
    hack_asm += [f"({true_label})", "@SP", "A=M-1", "M=-1", f"@{end_label}", "0;JMP"]

    # End label
    hack_asm += [f"({end_label})"]

    return hack_asm
    
    

hack_instructions = []
# Determine command type
for instruction in instructions:
    parts = instruction.split()
    command = parts[0]

    # Check for arithmetic/logical commands
    if command in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
        print(f"{instruction} is an Arithmetic Command")
        if command == "neg":
            hack_instructions.extend(handle_neg())
        if command == "not":
            hack_instructions.extend(handle_not())
        if command == "add":
            hack_instructions.extend(handle_add())
        if command == "sub":
            hack_instructions.extend(handle_sub())
        if command == "and":
            hack_instructions.extend(handle_and())
        if command == "or":
            hack_instructions.extend(handle_or())
        if command in ["eq", "gt", "lt"]:
            hack_instructions.extend(handle_comparison(command))

    # Check for push commands
    elif command == 'push':
        segment = parts[1]
        index = parts[2]
        print(f"{instruction} is a Push Command with segment: {segment}, index: {index}")
        if segment == "constant":
            hack_instructions.extend(push_constant(index))
        if segment in ["local", "argument", "this", "that"]:
            hack_instructions.extend(push_from_segment(segment, index))

    elif command == 'pop':
        segment = parts[1]
        index = parts[2]
        print(f"{instruction} is a Pop Command with segment: {segment}, index: {index}")
        if segment in ["local", "argument", "this", "that"]:
            hack_instructions.extend(pop_from_segment(segment, index))
    else:
        print(f"{instruction} is an Unknown Command")

# Write to output file
output_file = vm_file.replace('.vm', '.asm')
with open(output_file, 'w') as file:
    for hack_instruction in hack_instructions:
        file.write(hack_instruction + '\n')

