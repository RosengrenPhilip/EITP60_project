@ Minimal Cortex-M0 startup for ELMO targets.
@ ELMO reads the initial stack pointer and reset vector from the first two
@ words of the binary, and fills RAM with 0xFF before running, so we must
@ copy .data and zero .bss ourselves before calling main.

    .syntax unified
    .cpu cortex-m0
    .thumb

    .section .vectors, "a"
    .word _stack
    .word reset_handler

    .text
    .thumb_func
    .global reset_handler
reset_handler:
    @ Copy initialised data from ROM to RAM.
    ldr r0, =_data_loadaddr
    ldr r1, =_data
    ldr r2, =_edata
copy_data:
    cmp r1, r2
    bhs zero_bss
    ldr r3, [r0]
    str r3, [r1]
    adds r0, #4
    adds r1, #4
    b copy_data

zero_bss:
    ldr r1, =_bss
    ldr r2, =_ebss
    movs r3, #0
zero_loop:
    cmp r1, r2
    bhs start_main
    str r3, [r1]
    adds r1, #4
    b zero_loop

start_main:
    bl main
    bl endprogram
hang:
    b hang
