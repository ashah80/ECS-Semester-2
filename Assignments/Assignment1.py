import sys

# A stack class with push, pop, and peek methods (from class demo)
class Stack:
    pointer = -1
    def __init__(self, length):
        self.length = length
        self.stack = [None] * length
    def pop(self):
        if self.pointer == -1:
            print("Stack is empty", file=sys.stderr)
        value = self.stack[self.pointer]
        self.stack[self.pointer] = None
        self.pointer -= 1
        return value
    def push(self, value):
        if self.pointer == self.length - 1:
            print("Stack is full", file=sys.stderr)
            return
        self.pointer += 1
        self.stack[self.pointer] = value
    def peek(self):
        if self.pointer == -1:
            print("Stack is empty", file=sys.stderr)
        value = self.stack[self.pointer]
        return value
    
def add(stack):
    num1 = stack.pop()
    num2 = stack.pop()
    stack.push(num1 + num2)

    
# Get CLI arguments for txt file 
text_file = ""
if len(sys.argv) > 1:
    text_file = sys.argv[1]
else:
    print("Usage: my_script.py <input_file>", file=sys.stderr)
    sys.exit()

# Open and read the file
try:
    with open(text_file, 'r') as file:
        content = file.read()
        print(content)
    
except FileNotFoundError:
    print(f"Error: A FileNotFound error occurred", file=sys.stderr)
    sys.exit(1)

except IOError as e:
    print(f"Error: An I/O error occurred: {e}", file=sys.stderr)
    sys.exit(1)




# Implement add, sub, mult, and div methods




        
