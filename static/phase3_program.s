    ; 2026 Phase 3 Program
        ORG 0
        ldi   R5, 0x43        ; R5 = 0x43
        ldi   R5, 6(R5)       ; R5 = 0x49
        ld    R4, 0x89        ; R4 = (0x89) = 0xA7
        ldi   R4, 4(R4)       ; R4 = 0xAB
        ld    R0, -8(R4)      ; R0 = (0xA3) = 0x68
        ldi   R2, 4           ; R2 = 4
        ldi   R5, 0x87        ; R5 = 0x87
        brmi  R5, 3           ; continue with the next instruction (will not branch)
        ldi   R5, 5(R5)       ; R5 = 0x8C
        ld    R1, -3(R5)      ; R1 = (0x8C - 3) = 0xA7
        nop
        brpl  R1, 2           ; continue with the instruction at “target” (will branch)
        ldi   R3, 7(R5)       ; this instruction will not execute
        ldi   R7, -4(R3)      ; this instruction will not execute

target: add   R7, R5, R2      ; R7 = 0x90
        addi  R1, R1, 3       ; R1 = 0xAA
        neg   R1, R1          ; R1 = 0xFFFFFF56
        not   R1, R1          ; R1 = 0xA9
        andi  R1, R1, 0xF     ; R1 = 9
        ror   R4, R0, R2      ; R4 = 0x80000006
        ori   R1, R4, 5       ; R1 = 0x80000007
        shra  R4, R1, R2      ; R4 = 0xF8000000
        shr   R5, R5, R2      ; R5 = 0x8
        st    0xA3, R5        ; (0xA3) = 0x8 new value in memory with address 0xA3
        rol   R5, R0, R2      ; R5 = 0x680
        or    R7, R2, R0      ; R7 = 0x6C
        and   R4, R5, R0      ; R4 = 0
        st    0x89(R4), R7    ; (0x89) = 0x6C new value in memory with address 0x89
        sub   R0, R5, R7      ; R0 = 0x614
        shl   R4, R5, R2      ; R4 = 0x6800
        ldi   R7, 7           ; R7 = 7
        ldi   R3, 0x19        ; R3 = 0x19
        mul   R3, R7          ; HI = 0; LO = 0xAF
        mfhi  R1              ; R1 = 0
        mflo  R6              ; R6 = 0xAF
        div   R3, R7          ; HI = 4 , LO = 3
        ldi   R8, 2(R7)       ; R8 = 9 setting up argument registers
        ldi   R9, -4(R3)      ; R9 = 0x15 R8, R9, R10, and R11
        ldi   R10, 3(R6)      ; R10 = 0xB2
        ldi   R11, 5(R1)      ; R11 = 5
        jal   R10             ; subA address 0xB2 in R10 into PC; return address 0x29 into R12
        halt                  ; upon return, the program halts

subA:   ORG 0xB2              ; procedure subA
        add R14, R8, R10      ; R13 and R14 are return value registers
        sub R13, R9, R11      ; R14 = 0xBB, R13 = 0x10
        sub R14, R14, R13     ; R14 = 0xAB
        jr R12                ; return from subA procedure with address 0x29 in R12
               
        ORG   0x89            ; initialize memory as asked
        WORD  0xA7
        ORG   0xA3
        WORD  0x68
