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
        if '#' in line:
            line = line[:line.index('#')].strip()
        if line and not line.startswith('#'):
            instructions.append(line)
print(instructions)

# Helper functions for pushing and popping from the stack

def push_constant(value):
    """
    Pushes D onto stack.
    This function takes in a value, loads it into the D register, goes to the address of the stack pointer, stores the value in that memory address, increments stack pointer.
    """
    return [f"@{value}", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1"] 

def pop_from_stack():
    """
    Pops the top of the stack and stores in D.
    This function decrements the stack pointer, then stores the value at that memory address in the D register.
    """
    return ["@SP", "M=M-1", "A=M", "D=M"]
    



hack_instructions = []
# Determine command type
for instruction in instructions:
    parts = instruction.split()
    command = parts[0]

    if command in ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']:
        print(f"{instruction} is an Arithmetic Command")
    elif command == 'push':
        segment = parts[1]
        index = parts[2]
        print(f"{instruction} is a Push Command with segment: {segment}, index: {index}")
        if segment == "constant":
            hack_instructions.extend(push_constant(index))
    elif command == 'pop':
        segment = parts[1]
        index = parts[2]
        print(f"{instruction} is a Pop Command with segment: {segment}, index: {index}")
    else:
        print(f"{instruction} is an Unknown Command")

# Write to output file
output_file = vm_file.replace('.vm', '.asm')
with open(output_file, 'w') as file:
    for hack_instruction in hack_instructions:
        file.write(hack_instruction + '\n')

