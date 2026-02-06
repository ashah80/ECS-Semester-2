import sys

# Get CLI argument for vm file 
vm_file = ""
if len(sys.argv) == 1 and sys.argv[1].endswith('.vm'):
    vm_file = sys.argv[1]
else:
    print("Usage: Assignment1.py <input_file.vm>", file=sys.stderr)
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



