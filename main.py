import re
import argparse

class InvalidInstructionParsed(Exception):
    pass

register_mapping = {
    "zero":0, 
    "at":1, # modification to spec
    "t0":2,
    "t1":3, 
    "t2":4, 
    "t3":4, 
    "t4":5,
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
        raise InvalidInstructionParsed("idk man")
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
reg_label = ["brzr", "brnz", "brpl", "brmi"]
reg_offset_reg = ["ld", "ldi"]
offset_reg_reg = ["st"]
reg_reg = ["mul", "div", "not", "neg"]
reg = ["jal", "jr", "in", "out", "mflo", "mfhi"]
no_args = ["nop", "halt"]


def get_register_number(register_name: str) -> int:
    if register_name.lower() not in register_mapping.keys():
        raise InvalidInstructionParsed(f"invalid register number: {register_name}")
    
    return register_mapping[register_name.lower()]

def get_constant(constant_value: str) -> int:
    constant_value = constant_value.lower()

    if match := re.match(r"^0b(?P<number>[10]+)$", constant_value):
        value = int(match.groupdict()['number'], 2)

    elif match := re.match(r"^0x(?P<number>[0-9a-f]+)$", constant_value):
        value = int(match.groupdict()['number'], 16)

    elif match := re.match(r"^-\s*(?P<number>[0-9]+)$", constant_value):
        value = -int(match.groupdict()['number'], 10)

    elif match := re.match(r"^(?P<number>[0-9]+)$", constant_value):
        value = int(match.groupdict()['number'], 10)

    else:
        raise InvalidInstructionParsed(f"could not parse constant value: {constant_value}")

    if value > 0b011_1111_1111_1111_1111:
        raise InvalidInstructionParsed("constant value too large")
    
    if value < -(0b011_1111_1111_1111_1111+1):
        raise InvalidInstructionParsed("constant value too negative")
    
    return value & 0x7FFFF

def get_branch_offset(argument: str, labels: dict[str,int], instruction_number: int) -> int:
    if argument in labels.keys():
        return (labels[argument] - 1) - instruction_number
    
    return get_constant(argument)

def r_format(opcode: int, ra: int, rb: int, rc: int) -> int:
    return (opcode << 27) | (ra << 23) | (rb << 19) | (rc << 15) | 0

def i_format(opcode: int, ra: int, rb: int, c=0) -> int:
    return (opcode << 27) | (ra << 23) | (rb << 19) | c

def b_format(opcode: int, ra: int, c2: int, c: int):
    return (opcode << 27) | (ra << 23) | (c2 << 19) | c

def j_format(opcode: int, ra: int):
    return (opcode << 27) | (ra << 23) | 0

def m_format(opcode: int):
    return (opcode << 27) | 0

def parse_line(line: str, labels: dict[str,int], instruction_number: int) -> int:

    instruction_match = re.match(r"^\s*(?P<instruction>\w+)", line)
    if (instruction_match is None):
        raise InvalidInstructionParsed("couldn't get instruction name")
    
    instruction_name = instruction_match.groupdict()['instruction']

    if instruction_name not in opcodes:
        raise InvalidInstructionParsed(f"unknown instruction name: {instruction_name}")
    
    opcode = opcodes[instruction_name]

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
        match = re.match(r"^\s*\w+\s+(?P<ra>\w+)\s*,\s*(?P<rb>\w+)\s*,\s*(?P<const>[\w-]+)\s*$", line)
        if match is None:
            raise InvalidInstructionParsed(f"failed to parse reg reg const instruction: {line}")
        match_dict = match.groupdict()
        ra = get_register_number(match_dict['ra'])
        rb = get_register_number(match_dict['rb'])
        const = get_constant(match_dict['const'])
        return i_format(opcode, ra, rb, const)
    
    elif instruction_name in reg_label:
        #                                                 const can also be a label
        match = re.match(r"^\s*\w+\s+(?P<ra>\w+)\s*,\s*(?P<const>[\w-]+)\s*$", line)
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
        match = re.match(r"^\s*\w+\s+(?P<ra>\w+)\s*,\s*(?P<const>[\w-]+)\s*\(\s*(?P<rb>\w+)\s*\)\s*$", line)
        if match is None:
            # try matching without it
            match = re.match(r"^\s*\w+\s+(?P<ra>\w+)\s*,\s*(?P<const>[\w-]+)\s*$", line)
            if match is None:
                raise InvalidInstructionParsed(f"failed to parse reg offset reg instruction: {line}")

        match_dict = match.groupdict()
        ra = get_register_number(match_dict['ra'])
        rb = get_register_number(match_dict.get('rb', "r0"))
        const = get_constant(match_dict['const'])
        return i_format(opcode, ra, rb, const)

    elif instruction_name in offset_reg_reg:
        # also handle the r0 case
        match = re.match(r"^\s*\w+\s+(?P<const>[\w-]+)\s*\(\s*(?P<rb>\w+)\s*\)\s*,\s*(?P<ra>\w+)\s*$", line)
        if match is None:
            # try matching without it
            match = re.match(r"^\s*\w+\s+(?P<const>[\w-]+)\s*,\s*(?P<ra>\w+)\s*$", line)
            if match is None:
                raise InvalidInstructionParsed(f"failed to parse offset reg reg instruction: {line}")

        match_dict = match.groupdict()
        ra = get_register_number(match_dict['ra'])
        rb = get_register_number(match_dict.get('rb', "r0"))
        const = get_constant(match_dict['const'])
        return i_format(opcode, ra, rb, const)

    elif instruction_name in no_args:
        return m_format(opcode)

    else:
        raise InvalidInstructionParsed("instruction name is not valid")

def extract_labels_and_instruction(line: str) -> tuple[list[str],str]:
    labels = []
    while (True):
        line_match = re.match(r"^\s*(?P<label>\w+):(?P<rest>.*)", line)
        if (line_match is None):
            break

        labels.append(line_match.groupdict()["label"])
        line = line_match.groupdict()["rest"]
    
    return labels, line.strip()

def first_pass(code_string: str) -> tuple[dict[str,int], list[tuple[int,str]]]:

    code_lines_with_comments = code_string.splitlines()

    # remove comments
    code_lines = []
    for line in code_lines_with_comments:
        line_match = re.match(r"(?P<line_no_comment>.*?);.*", line)
        if line_match is not None:
            code_lines.append(line_match.groupdict()["line_no_comment"])
        else:
            code_lines.append(line)

    labels = {}
    instruction_list: list[tuple[int,str]] = []

    instruction_number = 0
    for line in code_lines:
        has_instruction = True
        line_labels, instruction = extract_labels_and_instruction(line)
        if instruction == "":
            has_instruction = False

        for label in line_labels:
            labels[label] = instruction_number

        if match := re.match(r"^\s*org\s+(?P<const>\w+)\s*$", instruction.lower()):
            instruction_number = get_constant(match.groupdict()['const'])
            continue
        
        if has_instruction:
            instruction_list.append((instruction_number, instruction))
            instruction_number += 1
    
    # read in the code from a text file
    # iterate over each line
        # check for labels
        # remember locations of offset in memory & value and store them somewhere
    return labels, instruction_list
    
def second_pass(labels: dict[str, int], instructions: list[tuple[int,str]]) -> list[tuple[int,int]]:
    encoded_instructions: list[tuple[int,int]] = []
    for instruction_number, line in instructions:
        encoded_instructions.append((instruction_number, parse_line(line, labels, instruction_number)))
        print(f"{instruction_number:02X} {parse_line(line, labels, instruction_number):08X}")

    return encoded_instructions

def assemble(code:str) -> list[tuple[int,int]]:
    labels, instructions = first_pass(code)
    return second_pass(labels, instructions)

# assemble("""
# target: add R3, R3, R1 ; R3 = 0x5D
#         addi R4, R4, 2 ; R4 = 0x99
#         neg R4, R4 ; R4 = 0xFFFFFF67
# label2: label3:
#         not R4, R4 ; R4 = 0x98
#         andi R4, R4, 0xF ; R4 = 8
#         ror R2, R0, R1 ; R2 = 0xC0000008
#         ori R4, R2, 7 ; R4 = 0xC000000F
# label4:
#         shra R2, R4, R1 ; R2 = 0xF8000001
# """)

if __name__ == "__main__":
    encoded_instructions = assemble("""
        ORG 0
        ldi   R3, 0x65        ; R3 = 0x65
        ldi   R3, 3(R3)       ; R3 = 0x68
        ld    R2, 0x54        ; R2 = (0x54) = 0x97
        ldi   R2, 1(R2)       ; R2 = 0x98
        ld    R0, -6(R2)      ; R0 = (0x92) = 0x46
        ldi   R1, 3           ; R1 = 3
        ldi   R3, 0x57        ; R3 = 0x57
        brmi  R3, 3           ; continue with the next instruction (will not branch)
        ldi   R3, 3(R3)       ; R3 = 0x5A
        ld    R4, -6(R3)      ; R4 = (0x5A - 6) = 0x97
        nop
        brpl  R4, 2           ; continue with the instruction at “target” (will branch)
        ldi   R6, 7(R3)       ; this instruction will not execute
        ldi   R5, -4(R6)      ; this instruction will not execute

target: add   R3, R3, R1      ; R3 = 0x5D
        addi  R4, R4, 2       ; R4 = 0x99
        neg   R4, R4          ; R4 = 0xFFFFFF67
        not   R4, R4          ; R4 = 0x98
        andi  R4, R4, 0xF     ; R4 = 8
        ror   R2, R0, R1      ; R2 = 0xC0000008
        ori   R4, R2, 7       ; R4 = 0xC000000F
        shra  R2, R4, R1      ; R2 = 0xF8000001
        shr   R3, R3, R1      ; R3 = 0xB
        st    0x92, R3        ; (0x92) = 0xB new value in memory with address 0x92
        rol   R3, R0, R1      ; R3 = 0x230
        or    R5, R1, R0      ; R5 = 0x47
        and   R2, R3, R0      ; R2 = 0
        st    0x54(R2), R5    ; (0x54) = 0x47 new value in memory with address 0x54
        sub   R0, R3, R5      ; R0 = 0x1E9
        shl   R2, R3, R1      ; R2 = 0x1180
        ldi   R5, 8           ; R5 = 8
        ldi   R6, 0x17        ; R6 = 0x17
        mul   R6, R5          ; HI = 0; LO = 0xB8
        mfhi  R4              ; R4 = 0
        mflo  R7              ; R7 = 0xB8
        div   R6, R5          ; HI = 7, LO = 2
        ldi   R10, 1(R5)      ; R10 = 9 setting up argument registers
        ldi   R11, -3(R6)     ; R11 = 0x14 R10, R11, R12, and R13
        ldi   R12, 1(R7)      ; R12 = 0xB9
        ldi   R13, 4(R4)      ; R13 = 4
        jal   R12             ; address of subroutine subA in R12 - return address in R8
        halt                  ; upon return, the program halts
 
subA:   ORG   0xB9            ; procedure subA
        add   R15, R10, R12   ; R14 and R15 are return value registers
        sub   R14, R11, R13   ; R15 = 0xC2, R14 = 0x10
        sub   R15, R15, R14   ; R15 = 0xB2
        jr    R8              ; return from procedure
               
    """)

    for instruction_number, instruction in encoded_instructions:
        print(f"{instruction_number:02X} {instruction:08X}")
    
    if max([instruction[0] for instruction in encoded_instructions]) >= 512:
        raise Exception("Program too long")
    
    instruction_dict: dict[int, int] = {}
    for instruction_number, instruction in encoded_instructions:
        if instruction_number in instruction_dict:
            raise Exception("Program overwrites itself (bad org statement)")
        instruction_dict[instruction_number] = instruction

    # Initialize memory locations 0x54 and 0x92 with the 32-bit hexadecimal values
    # 0x97 and 0x46, respectively. 
    instruction_dict[0x54] = 0x97
    instruction_dict[0x92] = 0x46

    with open("phase3_program.txt", "w") as f:
        for i in range(511):
            f.write(f"{instruction_dict.get(i, 0):08X}\n")

        f.write(f"{instruction_dict.get(512, 0):08X}")
        