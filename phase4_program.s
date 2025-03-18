ORG 0
    ; Initialize Registers
    ldi R3, 0x65       ; R3 = 0x65 
    ldi R3, 3(R3)      ; R3 = 0x68
    ld R2, 0x54        ; R2 = (0x54) = 0x97
    ldi R2, 1(R2)      ; R2 = 0x98
    ld R0, -6(R2)      ; R0 = (0x92) = 0x46
    ldi R1, 3          ; R1 = 3
    ldi R3, 0x57       ; R3 = 0x57
    brmi R3, 3         ; Continue with next instruction (no branch)
    ldi R3, 3(R3)      ; R3 = 0x5A
    ld R4, -6(R3)      ; R4 = (0x5A - 6) = 0x97
    nop
    brpl R4, 2         ; Branch to "target" (will branch)
    ldi R6, 7(R3)      ; This instruction will not execute
    ldi R5, -4(R6)     ; This instruction will not execute

; Target Label
target:
    add R3, R3, R1     ; R3 = 0x5D
    addi R4, R4, 2     ; R4 = 0x99
    neg R4, R4         ; R4 = 0xFFFFFF67
    not R4, R4         ; R4 = 0x98
    andi R4, R4, 0xF   ; R4 = 8
    ror R2, R0, R1     ; R2 = 0xC0000008
    ori R4, R2, 7      ; R4 = 0xC000000F
    shra R2, R4, R1    ; R2 = 0xF8000001
    shr R3, R3, R1     ; R3 = 0xB
    st 0x92, R3        ; (0x92) = 0xB (new memory value at 0x92)
    rol R3, R0, R1     ; R3 = 0x230
    or R5, R1, R0      ; R5 = 0x47  
    and R2, R3, R0     ; R2 = 0
    st 0x54(R2), R5    ; (0x54) = 0x47 (new memory value at 0x54)
    sub R0, R3, R5     ; R0 = 0x1E9
    shl R2, R3, R1     ; R2 = 0x1180

    ; Multiplication and Division Operations
    ldi R5, 8          ; R5 = 8
    ldi R6, 0x17       ; R6 = 0x17
    mul R6, R5         ; HI = 0; LO = 0xB8
    mfhi R4            ; R4 = 0
    mflo R7            ; R7 = 0xB8
    div R6, R5         ; HI = 7 , LO = 2

    ; Setting Up Argument Registers
    ldi R10, 1(R5)     ; R10 = 9
    ldi R11, -3(R6)    ; R11 = 0x14
    ldi R12, 1(R7)     ; R12 = 0xB9
    ldi R13, 4(R4)     ; R13 = 4
    jal R12            ; Jump to subA (R12), store return address in R8

    ; Loop and Display Logic
    in R4               ; Read switch input (SW[0] to SW[7] = 0xC0) into R4
    st 0x55, R4         ; Store for next iteration
    ldi R1, 0x2E        ; Address of loop
    ldi R7, 1           ; R7 = 1
    ldi R5, 40          ; Loop counter (40 iterations)

loop:
    out R4              ; Display R4 on 7-segment display
    ldi R5, -1(R5)      ; Decrement loop counter
    brzr R5, 8          ; If zero, branch to "done"
    ld R6, 0xF0         ; Load delay counter

loop2:
    ldi R6, -1(R6)      ; Decrement delay counter
    nop
    brnz R6, -3         ; Repeat delay if R6 ≠ 0
    
    shr R4, R4, R7      ; Shift R4 right
    brnz R4, -9         ; Repeat loop if R4 ≠ 0
    ld R4, 0x55         ; Reload initial value from address 0x55
    jr R1               ; Jump to loop

done:
    ldi R4, 0xAA        ; Final display value
    out R4              ; Display 0xAA
    halt                ; Halt execution


subA: ORG 0xB9          ; Subroutine: subA
    add R15, R10, R12   ; R15 = 0xC2
    sub R14, R11, R13   ; R14 = 0x10
    sub R15, R15, R14   ; R15 = 0xB2
    jr R8               ; Return from subroutine

ORG 0x54
WORD 0x97
ORG 0x92
WORD 0x46
ORG 0xF0
WORD 0xFFFF