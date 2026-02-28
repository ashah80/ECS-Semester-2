# Project 8: Advanced VM Translator

A Python-based VM translator for the Nand2Tetris course (Project 8) that converts VM code (including function calls and program control flow) into Hack assembly language.

## Usage

```bash
python Project8.py <input.vm or directory>
```

- If a directory is provided, all `.vm` files in the directory are translated, and a single `.asm` file is generated with the directory's name.
- If a single `.vm` file is provided, a corresponding `.asm` file is generated in the same directory.

## Supported Commands (from Project 7)

### Arithmetic/Logical

| Command | Description                                |
| ------- | ------------------------------------------ |
| `add`   | Pops two values, pushes their sum          |
| `sub`   | Pops two values, pushes x - y              |
| `neg`   | Negates the top value on the stack         |
| `eq`    | Pushes -1 (true) if x == y, else 0 (false) |
| `gt`    | Pushes -1 (true) if x > y, else 0 (false)  |
| `lt`    | Pushes -1 (true) if x < y, else 0 (false)  |
| `and`   | Bitwise AND of top two values              |
| `or`    | Bitwise OR of top two values               |
| `not`   | Bitwise NOT of top value                   |

### Memory Access

| Segment    | RAM Location | Description                          |
| ---------- | ------------ | ------------------------------------ |
| `constant` | N/A          | Pushes the constant value itself     |
| `local`    | LCL + index  | Function's local variables           |
| `argument` | ARG + index  | Function's arguments                 |
| `this`     | THIS + index | N/A                                  |
| `that`     | THAT + index | N/A                                  |
| `temp`     | 5 + index    | Fixed segment (RAM 5-12)             |
| `pointer`  | THIS/THAT    | 0 = THIS register, 1 = THAT register |
| `static`   | 16-255       | Named as `<filename>.<index>`        |

### Program Flow & Function Calling (Project 8)

| Command    | Description                                        |
| ---------- | -------------------------------------------------- |
| `label`    | Declares a label for goto/if-goto                  |
| `goto`     | Unconditional jump to a label                      |
| `if-goto`  | Conditional jump to a label (if top of stack != 0) |
| `function` | Declares a function and allocates local vars       |
| `call`     | Calls a function, handling argument/return setup   |
| `return`   | Returns from a function, restoring caller state    |

## Implementation Notes

- **Stack Pointer (SP)**: Stored at `RAM[0]`, points to the next available stack address (`RAM[256+]`).
- **Segment Pointers**: `LCL, ARG, THIS, THAT` store base addresses for their segments.
- **Bootstrap Code**: Initializes the stack and calls `Sys.init` if present.
- **Function Call/Return**: Handles saving/restoring caller frame, arguments, and return address. This architecture allows for recursion, nested function calling, etc (all with the elegance of a stack!).
- **Labels**: Each `eq`/`gt`/`lt` generates unique labels (e.g., `TRUE_0`, `END_0`). Each function also generates a unique return label based on a global counter.
