import sys
import os

# Get CLI argument for vm file/folder

if len(sys.argv) != 2:
    print("Usage: Project8.py <input.vm or directory>", file=sys.stderr)
    sys.exit()

input_path = sys.argv[1]
vm_files = []

# If single file
if os.path.isfile(input_path) and input_path.endswith(".vm"):
    vm_files = [input_path]
    output_file = input_path.replace(".vm", ".asm")
# If directory
elif os.path.isdir(input_path):
    for file in os.listdir(input_path):
        if file.endswith(".vm"):
            vm_files.append(os.path.join(input_path, file))

    output_file = os.path.join(input_path, os.path.basename(input_path) + ".asm")
else:
    print("Invalid input path", file=sys.stderr)
    sys.exit()

# Read from input file, avoid whitespace/comments, store in a list
all_instructions = []
for vm_file in vm_files:
    vm_basename = os.path.basename(vm_file).replace('.vm', '')

    with open(vm_file, 'r') as file:
        for line in file:
            line = line.strip()
            if '//' in line:
                line = line[:line.index('//')].strip()
            if line and not line.startswith('//'):
                all_instructions.append((vm_basename, line))

current_function = ""

# SP decrementer/incrementer helper function
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

def push_D_to_stack():
    """
    Pushes the value in the D register onto the stack.
    This function goes to the address of the stack pointer, stores the value in the D register in that memory address, increments stack pointer.
    """
    return ["@SP", "A=M", "M=D"] + increment_pointer()

# Helper functions for pushing and popping from the stack

def push_constant(value):
    """
    Pushes a value onto stack.
    This function takes in a value, loads it into the D register, goes to the address of the stack pointer, stores the value in that memory address, increments stack pointer.
    """
    return [f"@{value}", "D=A"] + push_D_to_stack()

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
    
    return [f"@{index}", "D=A", f"@{segment_pointers[segment]}", "A=D+M", "D=M"] + push_D_to_stack()

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
    
# Handle temp segment
def push_from_temp(index):
    """
    Pushes a value from the temp segment onto the stack.
    This function takes in an index, calculates the address of that index in the temp segment, stores the value at that memory address in the D register, then pushes that value onto the stack.
    """
    base_address = 5
    actual_address = str(base_address + int(index))
    return [f"@{actual_address}", "D=M"] + push_D_to_stack()

def pop_from_temp(index):
    """
    Pops a value from the stack and stores it in the temp segment.
    This function takes in an index, calculates the address of that index in the temp segment, pops a value from the stack (which is stored in the D register), then stores that value at the calculated memory address.
    """
    base_address = 5
    actual_address = str(base_address + int(index))
    return pop_from_stack() + [f"@{actual_address}", "M=D"]

# Handle pointer segment

def push_from_pointer(index):
    """
    Pushes a value from the pointer segment onto the stack.
    This function takes in an index, then pushes the value at THIS/THAT onto the stack.
    """
    if index == "0":
        return ["@THIS", "D=M"] + push_D_to_stack()
    elif index == "1":
        return ["@THAT", "D=M"] + push_D_to_stack()
    
def pop_from_pointer(index):
    """
    Pops a value from the stack and stores it in the pointer segment.
    This function takes in an index, then pops a value from the stack (which is stored in the D register) and stores that value at THIS/THAT.
    """
    if index == "0":
        return pop_from_stack() + ["@THIS", "M=D"]
    elif index == "1":
        return pop_from_stack() + ["@THAT", "M=D"]
    
# Handle static segment (RAM addresses 16-255, named based on file name and index)
def push_from_static(file_name, index):
    """
    Pushes a value from the static segment onto the stack.
    This function takes in an index, creates a variable based on the file name, stores the value at that memory address in the D register, then pushes that value onto the stack.
    """
    var_name = f"{file_name}.{index}"
    return [f"@{var_name}", "D=M"] + push_D_to_stack()

def pop_from_static(file_name, index):
    """
    Pops a value from the stack and stores it in the static segment.
    This function takes in an index, creates a variable based on the file name, pops a value from the stack (which is stored in the D register), then stores that value at the memory address of the variable.
    """
    var_name = f"{file_name}.{index}"
    return pop_from_stack() + [f"@{var_name}", "M=D"]

# Branching helper functions
def handle_label(label):
    """
    Returns a function-scoped label
    """
    return [f"({current_function}${label})"]

def handle_goto(label):
    """
    Returns assembly code for an unconditional goto statement.
    This function takes in a label, and returns assembly code that jumps to that label.
    """
    return [f"@{current_function}${label}", "0;JMP"]

def handle_if_goto(label):
    """
    Returns assembly code for a conditional goto statement.
    This function takes in a label, pops a value from the stack (which is stored in the D register), and returns assembly code that jumps to that label if the value is not equal to 0.
    """
    return pop_from_stack() + [f"@{current_function}${label}", "D;JNE"]

def handle_function_declaration(function_name, num_locals):
    """
    Returns assembly code for a function declaration.
    This function takes in a function name and number of local variables, creates a label for the function, and initializes the local variables to 0 on the stack.
    """

    hack_assembly = []
    # Label for the function declaration
    hack_assembly += [f"({function_name})"]
    for i in range(int(num_locals)):
        hack_assembly += push_constant(0)

    return hack_assembly

function_call_counter = 0
def handle_function_call(function_name, num_args):
    """
    Returns assembly code for a function call.
    This function takes in a function name and number of arguments, pushes the return address onto the stack, pushes the current LCL, ARG, THIS, THAT pointers onto the stack, repositions the ARG pointer, repositions the LCL pointer, jumps to the function, and declares a return label.
    """
    
    global function_call_counter
    hack_assembly = []

    # Push return address onto stack
    return_label = f"{current_function}$ret.{function_call_counter}"
    hack_assembly += [f"@{return_label}", "D=A"] + push_D_to_stack()
    function_call_counter += 1

    # Push LCL, ARG, THIS, THAT
    hack_assembly += ["@LCL", "D=M"] + push_D_to_stack()
    hack_assembly += ["@ARG", "D=M"] + push_D_to_stack()
    hack_assembly += ["@THIS", "D=M"] + push_D_to_stack()
    hack_assembly += ["@THAT", "D=M"] + push_D_to_stack()

    # Reposition ARG pointer: ARG = SP - num_args - 5 -> # ARG = SP - number_to_subtract 
    number_to_subtract = int(num_args) + 5
    hack_assembly += [f"@{number_to_subtract}", "D=A", "@SP", "D=M-D", "@ARG", "M=D"]

    # Reposition LCL pointer: LCL = SP
    hack_assembly += ["@SP", "D=M", "@LCL", "M=D"]

    # Jump to function
    hack_assembly += [f"@{function_name}", "0;JMP"]

    # Declare return label
    hack_assembly += [f"({return_label})"]

    return hack_assembly

def handle_function_return():
    """
    Returns assembly code for a function return.
    This function stores the return address in ARG, repositions the return value for the caller, restores the caller's SP, LCL, ARG, THIS, THAT pointers, and jumps to the return address.
    """
    hack_assembly = []

    # frame (stored in @R13) = LCL
    hack_assembly += ["@LCL", "D=M", "@R13", "M=D"]

    # retAddr (stored in @R14) = *(frame - 5)
    hack_assembly += ["@R13", "D=M", "@5", "A=D-A", "D=M", "@R14", "M=D"]

    # *ARG = pop()
    hack_assembly += pop_from_stack() + ["@ARG", "A=M", "M=D"]

    # SP = ARG + 1
    hack_assembly += ["@ARG", "D=M", "@SP", "M=D+1"]

    # THAT = *(frame - 1)
    hack_assembly += ["@R13", "D=M", "@1", "A=D-A", "D=M", "@THAT", "M=D"]

    # THIS = *(frame - 2)
    hack_assembly += ["@R13", "D=M", "@2", "A=D-A", "D=M", "@THIS", "M=D"]

    # ARG = *(frame - 3)
    hack_assembly += ["@R13", "D=M", "@3", "A=D-A", "D=M", "@ARG", "M=D"]

    # LCL = *(frame - 4)
    hack_assembly += ["@R13", "D=M", "@4", "A=D-A", "D=M", "@LCL", "M=D"]

    # goto retAddr
    hack_assembly += ["@R14", "A=M", "0;JMP"]

    return hack_assembly
    
hack_instructions = []
# SP initialization to 256
hack_instructions += ["@256", "D=A", "@SP", "M=D"]
# Only call Sys.init when translating a directory
if os.path.isdir(input_path):
    hack_instructions += handle_function_call("Sys.init", 0)

# Determine command type
for vm_basename, instruction in all_instructions:

    parts = instruction.split()
    command = parts[0]

    # Check for arithmetic/logical commands
    if command in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
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
        if segment == "constant":
            hack_instructions.extend(push_constant(index))
        if segment in ["local", "argument", "this", "that"]:
            hack_instructions.extend(push_from_segment(segment, index))
        if segment == "temp":
            hack_instructions.extend(push_from_temp(index))
        if segment == "pointer":
            hack_instructions.extend(push_from_pointer(index))
        if segment == "static":
            hack_instructions.extend(push_from_static(vm_basename, index))

    elif command == 'pop':
        segment = parts[1]
        index = parts[2]
        if segment in ["local", "argument", "this", "that"]:
            hack_instructions.extend(pop_from_segment(segment, index))
        if segment == "temp":
            hack_instructions.extend(pop_from_temp(index))
        if segment == "pointer":
            hack_instructions.extend(pop_from_pointer(index))
        if segment == "static":
            hack_instructions.extend(pop_from_static(vm_basename, index))

    # Check for branching commands
    elif command in ["label", "goto", "if-goto"]:
        label = parts[1]
        if command == "label":
            hack_instructions.extend(handle_label(label))
        if command == "goto":
            hack_instructions.extend(handle_goto(label))
        if command == "if-goto":
            hack_instructions.extend(handle_if_goto(label))
    
    # Check for function commands
    elif command == "function":
        function_name = parts[1]
        num_locals = parts[2]
        current_function = function_name
        hack_instructions.extend(handle_function_declaration(function_name, num_locals))

    elif command == "call":
        function_name = parts[1]
        num_args = parts[2]
        hack_instructions.extend(handle_function_call(function_name, num_args))

    elif command == "return":
        hack_instructions.extend(handle_function_return())

    else:
        print(f"Error: {instruction} is an Unknown Command", file=sys.stderr)

# Write to output file
with open(output_file, 'w') as file:
    for hack_instruction in hack_instructions:
        file.write(hack_instruction + '\n')