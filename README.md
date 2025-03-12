# ELEC374 MiniSRC Assembler
## Overview
The ELEC374 MiniSRC Assembler is a Python tool designed to translate assembly code written for the Mini SRC (a simple 32-bit RISC computer) into a hexadecimal dump of encoded instructions. The output is formatted for use with ModelSim’s $readmemh directive to load instructions into memory.

This assembler supports the following instructions:

- Register register to register (e.g., `add`, `sub`, `and`, `or`, `ror`, `rol`, `shr`, `shra`, `shl`)
- Register to register with constant immediate (e.g., `addi`, `andi`, `ori`)
- Branch instructions with labels (e.g., `brzr`, `brnz`, `brpl`, `brmi`)
- Load/store instructions with offset addressing (e.g., `ld`, `ldi`, `st`)
- Two-register operations (e.g., `mul`, `div`, `not`, `neg`)
- Single-register instructions (e.g., `jal`, `jr`, `in`, `out`, `mflo`, `mfhi`)
- No-argument instructions (e.g., `nop`, `halt`)


It also supports these assembler directives:
- `org <const value>`: Sets the current address for subsequent code
- `word <const value>`: Puts a specific constant value in memory at the current memory adress 

It works by performing two passes:

1. **First Pass:** Extracts labels and assigns instruction addresses (also handles org assembler directive).

2. **Second Pass:** Encodes each instruction into its 32-bit machine code representation. (also handles )
## Usage
### Prerequisites
- Python 3.6 or later.
- A text editor to write your assembly code.
- The assembly code should follow the syntax as described in the Mini SRC ISA specification.
### Running the Assembler
Open a terminal or command prompt and run the assembler with the following syntax:

```bash
python SRC-ASM.py <input_filename> -o <output_filename> [-v]
```

### Parameters:

- `<input_filename>`: The path to your assembly source file.
- `-o` or `--output`: The path for the output hex file. If omitted, the output file name will be derived from the input file name (with a .mem extension).
- `-v` or `--verbose`: Optional flag. When enabled, the assembler prints the encoded instruction (with addresses) to the console.
## Example
Assume you have an assembly file named `program.s`. To assemble this file and output the hex dump to `output.txt`, run:

```bash
python SRC-ASM.py program.s -o output.txt -v
```
If the `-o` option is omitted, the assembler will create an output file named `program.mem`.

## Output Format
The output file will contain 512 lines (one for each memory word from address 0 to 511) with each line displaying an 8-digit hexadecimal number representing the encoded 32-bit instruction or data. Unused memory locations will be filled with 00000000.

## Error Handling
**Invalid Instructions:** If an instruction or register is not recognized, the assembler will throw an error with details on the parsing failure.

**Memory Range:** The assembler checks that the highest address used does not exceed the available memory (512 words). If it does, an error is reported.

**Verbose Mode:** When running with -v, detailed traceback information is printed for easier debugging.
## Contact
For questions, bug reports, or feature requests, please contact:
asmhelp@davlaf.com
