class Stack:
    pointer = -1
    def __init__(self, length):
        self.length = length
        self.stack = [None] * length
    def pop(self):
        if self.pointer == -1:
            print("Stack is empty")
        value = self.stack[self.pointer]
        self.stack[self.pointer] = None
        self.pointer -= 1
        return value
    def push(self, value):
        if self.pointer == self.length - 1:
            print("Stack is full")
            return
        self.pointer += 1
        self.stack[self.pointer] = value
    def peek(self):
        if self.pointer == -1:
            print("Stack is empty")
        value = self.stack[self.pointer]
        return value
    
stack = Stack(5)
for i in range(6):
    stack.push(i)
    print(stack.peek())




        
