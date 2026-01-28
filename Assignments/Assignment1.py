import sys

class Stack:
    """
    A stack class with push, pop, and peek methods (from class demo)
    """
    def __init__(self, length):
        self.length = length
        self.stack = [None] * length
        self.pointer = -1
    def pop(self):
        if self.pointer == -1:
            print("Stack is empty, exiting", file=sys.stderr)
            exit(2)
        value = self.stack[self.pointer]
        self.stack[self.pointer] = None
        self.pointer -= 1
        return value
    def push(self, value):
        if self.pointer == self.length - 1:
            print("Stack is full, exiting", file=sys.stderr)
            exit(2)
        self.pointer += 1
        self.stack[self.pointer] = value
    def peek(self):
        if self.pointer == -1:
            print("Stack is empty, exiting", file=sys.stderr)
            exit(2)
        value = self.stack[self.pointer]
        return value

# Mathematical methods
def add(stack):
    num1 = stack.pop()
    num2 = stack.pop()
    stack.push(num1 + num2)

def sub(stack):
    num1 = stack.pop()
    num2 = stack.pop()
    stack.push(num2 - num1)

def mul(stack):
    num1 = stack.pop()
    num2 = stack.pop()
    stack.push(num2 * num1)

def div(stack):
    num1 = stack.pop()
    num2 = stack.pop()
    stack.push(num2 // num1)
    
# Get CLI argument for txt file 
text_file = ""
if len(sys.argv) > 1:
    text_file = sys.argv[1]
else:
    print("Usage: Assignment1.py <input_file>", file=sys.stderr)
    sys.exit()

# Open and read the file
try:
    with open(text_file, 'r') as file:
        command_list = file.read().split('\n')
        # Create 100-length stack
        stack = Stack(100)
        
        line_number = 0
        for command in command_list:
            line_number += 1
            if command.startswith('push '):
                number = int(command.split(' ')[1])
                stack.push(number)
            elif command == 'pop':
                stack.pop()
            elif command == 'add':
                add(stack)
            elif command == 'sub':
                sub(stack)
            elif command == 'mul':
                mul(stack)
            elif command == 'div':
                div(stack)
            else:
                print(f"Error at line number: {line_number}", file=sys.stderr)

        # Print to stdout
        print("Final top of stack:", stack.peek(), file=sys.stdout)
        
except FileNotFoundError:
    print(f"Error: A FileNotFound error occurred", file=sys.stderr)
    sys.exit(1)

except IOError as e:
    print(f"Error: An I/O error occurred: {e}", file=sys.stderr)
    sys.exit(1)



        
