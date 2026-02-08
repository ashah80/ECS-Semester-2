# Project 7: VM Translator

A Python-based VM translator for the Nand2Tetris course that converts VM code into Hack assembly language.

## Usage

```bash
python Project7.py <filename>.vm
```

This generates a `.asm` file with the same name in the same directory.

## Supported Commands

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

## Implementation Notes

- **Stack Pointer (SP)**: Stored at `RAM[0]`, Points to the next available stack address (`RAM[256+]`)
- **Segment Pointers**: `LCL, ARG, THIS, THAT` store base addresses for their segments
- **R13 Temp Register**: Used to store computed addresses during pop operations
- **Comparison Labels**: Each `eq`/`gt`/`lt` generates unique labels (such as `TRUE_0`, `END_0`)
