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
               
        ORG   0x54 ; initialize memory as asked
first_number:
        WORD  0x97
        ORG   0x92
second_number:
        WORD  0x46

        st first_number, r3