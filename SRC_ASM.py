import re
import argparse
import traceback

class InvalidInstructionParsed(Exception):
    pass

register_mapping = {
    "t0":0, 
    "at":1, # modification of spec
    "t1":2,
    "t2":3, 
    "t3":4, 
    "t4":5, 
    "t5":6, 
    "t6":7,
    "ra":8, 
    "sp":9, 
    "a0":10, 
    "a1":11, 
    "a2":12, 
    "a3":13, 
    "v0":14, 
    "v1":15, 

    "r0":0,
    "r1":1,
    "r2":2,
    "r3":3,
    "r4":4,
    "r5":5,
    "r6":6,
    "r7":7,
    "r8":8,
    "r9":9,
    "r10":10,
    "r11":11,
    "r12":12,
    "r13":13,
    "r14":14,
    "r15":15,
}

def get_c2_for_branch(branch_name: str) -> int:
    c2_values = {
        "brzr": 0b0000,
        "brnz": 0b0001, 
        "brpl": 0b0010, 
        "brmi": 0b0011, 
    }
    if branch_name not in c2_values.keys():
        raise InvalidInstructionParsed("invalid branch c2 value")
    return c2_values[branch_name]

opcodes = {
    "ld":    0b00000,
    "ldi":   0b00001,
    "st":    0b00010,
    "add":   0b00011,
    "sub":   0b00100,
    "and":   0b00101,
    "or":    0b00110,
    "ror":   0b00111,
    "rol":   0b01000,
    "shr":   0b01001,
    "shra":  0b01010,
    "shl":   0b01011,
    "addi":  0b01100,
    "andi":  0b01101,
    "ori":   0b01110,
    "div":   0b01111,
    "mul":   0b10000,
    "neg":   0b10001,
    "not":   0b10010,
    "jal":   0b10100,
    "jr":    0b10101,        
    "in":    0b10110,
    "out":   0b10111,
    "mflo":  0b11000,
    "mfhi":  0b11001,
    "nop":   0b11010,
    "halt":  0b11011,
    "brzr":  0b10011,
    "brnz":  0b10011,
    "brpl":  0b10011,
    "brmi":  0b10011,
}

reg_reg_reg = ["add", "sub", "and", "or", "ror", "rol", "shr", "shra", "shl"]
reg_reg_const = ["addi", "andi", "ori"]
reg_const = ["brzr", "brnz", "brpl", "brmi"]
reg_offset_reg = ["ld", "ldi"]
offset_reg_reg = ["st"]
reg_reg = ["mul", "div", "not", "neg"]
reg = ["jal", "jr", "in", "out", "mflo", "mfhi"]
no_args = ["nop", "halt"]


def get_register_number(register_name: str) -> int:
    if register_name.lower() not in register_mapping.keys():
        raise InvalidInstructionParsed(f"invalid register identifier: {register_name}")
    
    return register_mapping[register_name.lower()]

def get_constant(constant_value: str, labels: dict[str,int], bit_width: int = 19) -> int:
    is_signed = True

    if constant_value in labels:
        return labels[constant_value]

    constant_value = constant_value.lower()

    if match := re.match(r"^0b(?P<number>[10]+)$", constant_value):
        is_signed = False
        value = int(match.groupdict()['number'], 2)

    elif match := re.match(r"^0x(?P<number>[0-9a-f]+)$", constant_value):
        is_signed = False
        value = int(match.groupdict()['number'], 16)

    elif match := re.match(r"^-\s*(?P<number>[0-9]+)$", constant_value):
        value = -int(match.groupdict()['number'], 10)

    elif match := re.match(r"^(?P<number>[0-9]+)$", constant_value):
        value = int(match.groupdict()['number'], 10)
    else:
        raise InvalidInstructionParsed(f"could not parse constant value: {constant_value}")

    max_unsigned_value = 2**bit_width - 1
    max_signed_value = 2**(bit_width-1) - 1
    min_signed_value = -2**(bit_width-1)

    if (not is_signed):
        if value < 0:
            raise InvalidInstructionParsed(f"unsigned value {constant_value} (decimal {value}) is negative??")
        elif value > max_unsigned_value:
            raise InvalidInstructionParsed(f"unsigned value {constant_value} (decimal {value}) is above the maximum of {max_unsigned_value}")
        else:
            if value > max_signed_value:
                print(f"WARNING: unsigned constant value {constant_value} will be treated as negative by CPU")
            return value
        
    # value is signed
    
    if value > max_signed_value:
        raise InvalidInstructionParsed(f"signed constant value {constant_value} (decimal {value}) above the max value of {max_signed_value}")

    if value < min_signed_value:
        raise InvalidInstructionParsed(f"signed constant value {constant_value} (decimal {value}) below the min value of {min_signed_value}")

    return value

def get_branch_offset(argument: str, labels: dict[str,int], instruction_number: int) -> int:
    if argument in labels.keys():
        return (labels[argument] - 1) - instruction_number
    
    try:
        return get_constant(argument, labels)
    except InvalidInstructionParsed as e:
        raise InvalidInstructionParsed(f"{str(e)}\nMaybe you misspelled a label?")

def validate_opcode(opcode: int) -> bool:
    if 0 <= opcode < 0b11111:
        return True
    raise InvalidInstructionParsed(f"Opcode outside of range: {opcode}")

def r_format(opcode: int, ra: int, rb: int, rc: int) -> int:
    return (opcode << 27) | (ra << 23) | (rb << 19) | (rc << 15) | 0

def i_format(opcode: int, ra: int, rb: int, c: int =0) -> int:
    return (opcode << 27) | (ra << 23) | (rb << 19) | c & 0x7FFFF

def b_format(opcode: int, ra: int, c2: int, c: int) -> int:
    return (opcode << 27) | (ra << 23) | (c2 << 19) | c & 0x7FFFF

def j_format(opcode: int, ra: int) -> int:
    return (opcode << 27) | (ra << 23) | 0

def m_format(opcode: int) -> int:
    return (opcode << 27) | 0

def parse_line(line: str, labels: dict[str,int], instruction_number: int) -> int:

    instruction_match = re.match(r"^\s*(?P<instruction>\w+)", line)
    if (instruction_match is None):
        raise InvalidInstructionParsed("couldn't get instruction name")
    
    instruction_name = instruction_match.groupdict()['instruction']

    if instruction_name not in opcodes:
        raise InvalidInstructionParsed(f"unknown instruction name: {instruction_name}")
    
    opcode = opcodes[instruction_name]
    validate_opcode(opcode)

    if instruction_name in reg_reg_reg:
        match = re.match(r"^\s*\w+\s+(?P<ra>\w+)\s*,\s*(?P<rb>\w+)\s*,\s*(?P<rc>\w+)\s*$", line)
        if match is None:
            raise InvalidInstructionParsed(f"failed to parse reg reg reg instruction: {line}")
        match_dict = match.groupdict()
        ra = get_register_number(match_dict['ra'])
        rb = get_register_number(match_dict['rb'])
        rc = get_register_number(match_dict['rc'])
        return r_format(opcode, ra, rb, rc)

    elif instruction_name in reg_reg_const:
        match = re.match(r"^\s*\w+\s+(?P<ra>\w+)\s*,\s*(?P<rb>\w+)\s*,\s*(?P<const>[\w \-]+)\s*$", line)
        if match is None:
            raise InvalidInstructionParsed(f"failed to parse reg reg const instruction: {line}")
        match_dict = match.groupdict()
        ra = get_register_number(match_dict['ra'])
        rb = get_register_number(match_dict['rb'])
        const = get_constant(match_dict['const'], labels)
        return i_format(opcode, ra, rb, const)
    
    elif instruction_name in reg_const:
        #                                                 const can also be a label
        match = re.match(r"^\s*\w+\s+(?P<ra>\w+)\s*,\s*(?P<const>[\w \-]+)\s*$", line)
        if match is None:
            raise InvalidInstructionParsed(f"failed to parse reg label instruction: {line}")
        match_dict = match.groupdict()
        ra = get_register_number(match_dict['ra'])
        c2 = get_c2_for_branch(instruction_name) # could be error?
        const = get_branch_offset(match_dict['const'], labels, instruction_number) # could be a label
        return b_format(opcode, ra, c2, const)

    elif instruction_name in reg:
        match = re.match(r"^\s*\w+\s+(?P<ra>\w+)\s*$", line)
        if match is None:
            raise InvalidInstructionParsed(f"failed to parse reg instruction: {line}")
        match_dict = match.groupdict()
        ra = get_register_number(match_dict['ra'])
        return j_format(opcode, ra)
    
    elif instruction_name in reg_reg:
        match = re.match(r"^\s*\w+\s+(?P<ra>\w+)\s*,\s*(?P<rb>\w+)\s*$", line)
        if match is None:
            raise InvalidInstructionParsed(f"failed to parse reg reg instruction: {line}")
        match_dict = match.groupdict()
        ra = get_register_number(match_dict['ra'])
        rb = get_register_number(match_dict['rb'])
        return i_format(opcode, ra, rb)

    elif instruction_name in reg_offset_reg:
        # also handle the r0 case
        match = re.match(r"^\s*\w+\s+(?P<ra>\w+)\s*,\s*(?P<const>[\w \-]+)\s*\(\s*(?P<rb>\w+)\s*\)\s*$", line)
        if match is None:
            # try matching without it
            match = re.match(r"^\s*\w+\s+(?P<ra>\w+)\s*,\s*(?P<const>[\w \-]+)\s*$", line)
            if match is None:
                raise InvalidInstructionParsed(f"failed to parse reg offset reg instruction: {line}")

        match_dict = match.groupdict()
        ra = get_register_number(match_dict['ra'])
        rb = get_register_number(match_dict.get('rb', "r0"))
        const = get_constant(match_dict['const'], labels)
        return i_format(opcode, ra, rb, const)

    elif instruction_name in offset_reg_reg:
        # also handle the r0 case
        match = re.match(r"^\s*\w+\s+(?P<const>[\w \-]+)\s*\(\s*(?P<rb>\w+)\s*\)\s*,\s*(?P<ra>\w+)\s*$", line)
        if match is None:
            # try matching without it
            match = re.match(r"^\s*\w+\s+(?P<const>[\w \-]+)\s*,\s*(?P<ra>\w+)\s*$", line)
            if match is None:
                raise InvalidInstructionParsed(f"failed to parse offset reg reg instruction: {line}")

        match_dict = match.groupdict()
        ra = get_register_number(match_dict['ra'])
        rb = get_register_number(match_dict.get('rb', "r0"))
        const = get_constant(match_dict['const'], labels)
        return i_format(opcode, ra, rb, const)

    elif instruction_name in no_args:
        return m_format(opcode)

    else:
        raise InvalidInstructionParsed("instruction name is not valid")

def extract_labels_and_instruction(line: str) -> tuple[list[str],str]:
    labels: list[str] = []
    while (True):
        line_match = re.match(r"^\s*(?P<label>\w+):(?P<rest>.*)", line)
        if (line_match is None):
            break

        labels.append(line_match.groupdict()["label"])
        line = line_match.groupdict()["rest"]
    
    return labels, line.strip()

def first_pass(code_string: str) -> tuple[dict[str,int], list[tuple[int,str]], list[tuple[int,str]]]:

    code_lines_with_comments = code_string.splitlines()

    labels: dict[str, int] = {}
    instruction_list: list[tuple[int,str]] = []
    comments: list[tuple[int,str]] = []

    instruction_number = 0
    for line_with_comment in code_lines_with_comments:
        line_match = re.match(r"(?P<line_no_comment>.*?);(?P<comment>.*)", line_with_comment)
        line: str
        comment: str = ""
        if line_match is not None:
            line = line_match.groupdict()["line_no_comment"]
            comment = line_match.groupdict()["comment"]
        else:
            line = line_with_comment

        line_labels, instruction = extract_labels_and_instruction(line)

        line_has_instruction = True # directives don't count as instructions

        if instruction == "":
            line_has_instruction = False

        # check for assembler directives that do special behavior
        # check for org first
        if match := re.match(r"^\s*org\s+(?P<const>[\w \-]+)\s*$", instruction.lower()):
            line_has_instruction = False
            org_value = get_constant(match.groupdict()['const'], labels)
            if (org_value > 511):
                raise InvalidInstructionParsed(f"org value {match.groupdict()['const']} (decimal {org_value}) is above the maximum of 511")
            if (org_value < 0):
                raise InvalidInstructionParsed(f"org value {match.groupdict()['const']} (decimal {org_value}) must be above 0")
            
            instruction_number = org_value
        
        # add comment after org directive changes inst number
        if comment != "":
            comments.append((instruction_number, comment))

        for label in line_labels:
            if label not in labels:
                labels[label] = instruction_number
            else:
                raise InvalidInstructionParsed(f"Duplicate labels with name: {label}")

        if not line_has_instruction:
            continue
        
        instruction_list.append((instruction_number, instruction))
        instruction_number += 1

    return labels, instruction_list, comments
    
def second_pass(labels: dict[str, int], instructions: list[tuple[int,str]]) -> list[tuple[int,int]]:
    memory_entries: list[tuple[int,int]] = []
    for memory_address, instruction in instructions:

        # assembler directives to change memory data
        if match := re.match(r"^\s*word\s+(?P<const>\w+)\s*$", instruction.lower()):
            constant = get_constant(
                match.groupdict()['const'],
                labels,
                bit_width=32,
            )
            memory_entries.append((memory_address, constant))
            continue

        memory_entries.append((memory_address, parse_line(instruction, labels, memory_address)))

    return memory_entries

def assemble(code:str) -> tuple[dict[str, int], list[tuple[int, str]], list[tuple[int, str]], list[tuple[int,int]]]:
    labels, instructions, comments = first_pass(code)
    return labels, instructions, comments, second_pass(labels, instructions)

def assembly_to_file(file_extension: str, file_string: str):
    labels, instructions, comments, encoded_instructions = assemble(file_string)

    comment_dict: dict[int, list[str]] = {}
    for address, comment in comments:
        if address in comment_dict:
            comment_dict[address].append(comment)
        else:
            comment_dict[address] = [comment]

    instruction_dict: dict[int, str] = {}
    for address, instruction in instructions:
        instruction_dict[address] = instruction

    label_dict: dict[int, list[str]] = {}
    for label, address in labels.items():
        if address in label_dict:
            label_dict[address].append(label)
        else:
            label_dict[address] = [label]

    if max([instruction[0] for instruction in encoded_instructions]) >= 512:
        raise Exception("Program too long")
        
    memory: dict[int, int] = {}
    for instruction_number, instruction in encoded_instructions:
        if instruction_number in memory:
            raise Exception("Program overwrites itself (bad org statement)")
        memory[instruction_number] = instruction

    file_contents: str
    if file_extension == "mif":
        file_contents = mif_format(instruction_dict, label_dict, comment_dict, memory)
    else:
        file_contents = mem_format(instruction_dict, label_dict, comment_dict, memory)
    return encoded_instructions,file_contents

def mem_format(instruction_dict: dict[int, str], label_dict: dict[int, list[str]], comment_dict: dict[int, list[str]], memory: dict[int, int]) -> str:
    output: str
    output = "// Created with SRC-ASM (https://github.com/davlaf/elec374-assembler)\n"
    for i in range(512):
        if label_list := label_dict.get(i):
            output += "".join([f"//   {label}:\n" for label in label_list])
        output += (f"{f'@{i:X}'.rjust(4, ' ')} {memory.get(i, 0):08X}")

        line_comment = ""
        if instruction := instruction_dict.get(i):
            line_comment += (f"{instruction.ljust(18)}")
        if comment_list := comment_dict.get(i):
            line_comment += f"; {' ; '.join([comment.strip() for comment in comment_list])}"

        if line_comment != "":
            output += f" // {line_comment}"
        output += "\n"
    output += ("// Created with SRC-ASM (https://github.com/davlaf/elec374-assembler)")
    return output

def mif_format(instruction_dict: dict[int, str], label_dict: dict[int, list[str]], comment_dict: dict[int, list[str]], memory: dict[int, int]) -> str:
    output = """-- Created with SRC-ASM (https://github.com/davlaf/elec374-assembler)
WIDTH=32;
DEPTH=512;
 
ADDRESS_RADIX=HEX;
DATA_RADIX=HEX;
 
CONTENT BEGIN
"""
    for i in range(512):
        if label_list := label_dict.get(i):
            output += "".join([f"--   {label}:\n" for label in label_list])
        output += (f"{f'{i:X}'.rjust(3, ' ')}: {memory.get(i, 0):08X};")

        line_comment = ""
        if instruction := instruction_dict.get(i):
            line_comment += (f"{instruction.ljust(18)}")
        if comment_list := comment_dict.get(i):
            line_comment += f"; {' ; '.join([comment.strip() for comment in comment_list])}"

        if line_comment != "":
            output += f" -- {line_comment}"
        output += "\n"
    output += "END;\n"
    output += "-- Created with SRC-ASM (https://github.com/davlaf/elec374-assembler)\n"
    return output

def main():
    parser = argparse.ArgumentParser(
                    prog='ELEC374 MiniSRC Assembler',
                    usage='python SRC-ASM.py <input path> -o <output path> -t [mem|mif]',
                    description='Takes an assembly file and produces a hex dump of the encoded instructions, with syntax supported by modelsim to allow it to be added into the memory with the $readmemh',
                    epilog='Contact asmhelp@davlaf.com if you have questions or to report bugs, or raise a github Issue')

    parser.add_argument('filename') # input filename
    parser.add_argument('-o', '--output')      # output filename
    parser.add_argument('-v', '--verbose',
                    action='store_true')  # on/off flag
    parser.add_argument('-t', '--type', default="mem", choices=["mem", "mif"])
    args = parser.parse_args()
    input_filename: str = args.filename
    file_extension: str = args.type
    is_verbose: bool = args.verbose
    
    try:
        if args.output is None:
            if match := re.match(r"^(.*)\..*?$", input_filename):
                output_filename = f"{match.groups()[0]}.{file_extension}"
            else:
                output_filename = f"{input_filename}.{file_extension}"  
        else:
            output_filename: str = args.output
            # check if the file extension is different from the type argument
            if match := re.match(r"^.*\.(.*?)$", args.output):
                output_filename_file_extension = match.groups()[0]
                if output_filename_file_extension != file_extension:
                    print("Warning: Output filename and specified file type don't match")

        file_string: str
        with open(input_filename, "r", encoding="utf8") as f:
            file_string = f.read()
        
        encoded_instructions, file_contents = assembly_to_file(file_extension, file_string)

        if is_verbose:
            for instruction_number, instruction in encoded_instructions:
                print(f"{instruction_number:02X} {instruction:08X}")

        with open(output_filename, "w") as f:
            f.write(file_contents.encode("ascii", errors="ignore").decode())
            
        # not necessarily instructions if the word directive is used
        print(f"Successfully wrote {len(encoded_instructions)} data words to {output_filename}")
    except Exception as e:
        if is_verbose:
            print(traceback.format_exc())
        else:
            print(f"Error when assembling: {e}")

if __name__ == "__main__":
    main()