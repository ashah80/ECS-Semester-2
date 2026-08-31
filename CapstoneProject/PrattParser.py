# Pratt Parser: Implementation based on article: https://matklad.github.io/2020/04/13/simple-but-powerful-pratt-parsing.html

# Helper functions
def write_vm_arithmetic(file, command):
    file.write(f"{command}\n")

def write_vm_call(file, name, n_args):
    file.write(f"call {name} {n_args}\n")

def write_vm_push(file, segment, index):
    file.write(f"push {segment} {index}\n")

# Maps each operator to its (left_binding_power, right_binding_power) tuple. A higher number = tighter binding. The left and right binding powers are used to determine how operators of the same precedence are grouped (left-associative vs right-associative).
# If left_binding_power < right_binding_power, the operator is left-associative.
INFIX_BINDING_POWER = {
    '=': (1, 2),
    '|': (3, 4),
    '&': (5, 6),
    '<': (7, 8),
    '>': (7, 8),
    '+': (9, 10),
    '-': (9, 10), # same precedence as +
    '*': (11, 12),
    '/': (11, 12), # same precedence as *
}

# Unary operators only have a right bp
PREFIX_BINDING_POWER = {
    '-': 13, # unary minus has higher precedence than multiplication/division
    '~': 13, # bitwise NOT has same precedence as unary minus
}

class PrattParserMixin:

    # Return left and right binding powers for the given operator, or None if it's not an infix operator. Returning None is how we know to stop parsing infix operators.
    def infix_binding_power(self, operator):
        return INFIX_BINDING_POWER.get(operator, None)
    
    def prefix_binding_power(self, operator):
        return PREFIX_BINDING_POWER.get(operator, None)


    def compile_and_emit_expression(self):
        """
        Call compile_expression and emit the result if it was a constant, because compile_expression pushes off emitting constants so that they can be folded with adjacent operators. At the end of the expression, if we still have a constant value, we need to emit it onto the stack.
        """
        result = self.compile_expression()
        if result is not None:
            write_vm_push(self.vm_file, 'constant', result)

    def compile_expression(self, min_binding_power=0):
        """
        A replacement for the Project 11 compile_expression() function. min_binding_power is used to determine when to stop parsing infix operators. We keep parsing infix operators as long as their left binding power is greater than or equal to min_binding_power. When we encounter an operator with a lower binding power, we stop and return to the caller, which will then handle the next operator.
        """
        # Start by parsing the first term on the left hand side.
        left_side = self.compile_term()

        # Loop to parse any infix operators that follow. We keep parsing as long as the next operator has a binding power >= min_binding_power.
        while True:
            op_token = self.get_current_token()

            # If no more tokens, stop
            if op_token is None:
                break
            op = op_token[1] # get the actual token value

            binding_power = self.infix_binding_power(op)
            if binding_power is None:
                break

            left_bp, right_bp = binding_power

            # If this operator's left binding power is less than the min, it means that the operator to the left of this one has higher precedence, so we should stop parsing and return to the caller to handle this operator.
            if left_bp < min_binding_power:
                break

            # Consume operator
            self.consume_token(expected_type='symbol')

            # Recursively parse the right hand side of this operator, using the right binding power as the new min_binding_power. This ensures that any operators on the right hand side with higher precedence will be parsed before we emit the VM code for this operator.
            right_side = self.compile_expression(right_bp)

            # if both sides are constants, we can fold at compile time and just return the result
            if left_side is not None and right_side is not None:
                if op == '+':   left_side = left_side + right_side
                elif op == '-': left_side = left_side - right_side
                elif op == '*': left_side = left_side * right_side
                elif op == '/': left_side = left_side // right_side # use floor division for integers
                elif op == '&': left_side = left_side & right_side
                elif op == '|': left_side = left_side | right_side
                elif op == '<': left_side = -1 if left_side < right_side else 0
                elif op == '>': left_side = -1 if left_side > right_side else 0
                elif op == '=': left_side = -1 if left_side == right_side else 0
                # Don't emit any VM code since we can continue folding

            else: # at least one side is not a constant
                # if the left side is a constant but the right side isn't, we need to push the left constant onto the stack so that we can perform the operation at runtime
                if left_side is not None:
                    write_vm_push(self.vm_file, 'constant', left_side)

                # if the right side isn't a constant, the recursive call to compile_expression already emitted the VM code to compute its value and push it onto the stack. But if it is a constant, we need to push it onto the stack now.
                if right_side is not None:
                    write_vm_push(self.vm_file, 'constant', right_side)

                self.emit_binary_op(op)
                left_side = None # after emitting the VM code for this operator, the result is no longer a constant, so we set left_side to None to indicate that we can no longer fold with it

        return left_side # return the left side, which may be a constant if we were able to fold, or None if not

    # Write the VM code for the given binary operator. This is called after we've parsed the left and right hand sides of the operator, so we know what operation to perform on the values on the stack and in which order.
    def emit_binary_op(self, op):
        if op == '+':   write_vm_arithmetic(self.vm_file, 'add')
        elif op == '-': write_vm_arithmetic(self.vm_file, 'sub')
        elif op == '*': write_vm_call(self.vm_file, 'Math.multiply', 2)
        elif op == '/': write_vm_call(self.vm_file, 'Math.divide', 2)
        elif op == '&': write_vm_arithmetic(self.vm_file, 'and')
        elif op == '|': write_vm_arithmetic(self.vm_file, 'or')
        elif op == '<': write_vm_arithmetic(self.vm_file, 'lt')
        elif op == '>': write_vm_arithmetic(self.vm_file, 'gt')
        elif op == '=': write_vm_arithmetic(self.vm_file, 'eq')


