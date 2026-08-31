# String constant pooling optimization: instead of allocating a new String object every time a string literal appears, we allocate each unique string once as a static variable and reuse it everywhere it appears.

# Helper functions
def write_vm_function(file, name, n_locals):
    file.write(f"function {name} {n_locals}\n")

def write_vm_push(file, segment, index):
    file.write(f"push {segment} {index}\n")

def write_vm_call(file, name, n_args):
    file.write(f"call {name} {n_args}\n")

def write_vm_pop(file, segment, index):
    file.write(f"pop {segment} {index}\n")

def write_vm_return(file):
    file.write("return\n")

class StringPoolMixin:

    def find_string_literals(self):
        """
        The first pass. Go through all the tokens before compilation and find every unique string literal, assigning each one a static index, which is where the String object will be during runtime.
        """
        self.string_pool = {}
        self.unique_string_count = 0

        # Go through all the tokens and find string literals
        for token_type, token_value in self.tokens:
            if token_type == "stringConstant":
                # If we haven't seen this string literal before, add it to the string pool with a new index
                if token_value not in self.string_pool:
                    self.string_pool[token_value] = self.unique_string_count
                    self.unique_string_count += 1

    def compile_string_pool(self):
        """
        The second pass. After finding all the unique string literals, write VM code to allocate every unique string literal as a static variable at the beginning of the compiled output.
        """
        
        if self.unique_string_count == 0:
            return  # No string literals, so no need to compile anything
                
        # Function to initialize the string pool. We call this at the beginning of the constructor of each class.
        write_vm_function(self.vm_file, name=f"{self.class_name}.stringInitialization", n_locals=0)

        for string_value, static_index in self.string_pool.items():
            # Allocate a new string of the right length
            write_vm_push(self.vm_file, segment="constant", index=len(string_value))
            write_vm_call(self.vm_file, name="String.new", n_args=1)

            # Append each character to the string
            for char in string_value:
                write_vm_push(self.vm_file, segment="constant", index=ord(char))
                write_vm_call(self.vm_file, name="String.appendChar", n_args=2)

            # Store the string in the static variable
            write_vm_pop(self.vm_file, segment="static", index=static_index)

        # After initializing the string pool, we need to return from the function
        write_vm_push(self.vm_file, segment="constant", index=0)
        write_vm_return(self.vm_file)



        


        