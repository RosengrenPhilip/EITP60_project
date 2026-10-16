/* Linker script for ELMO targets (STM32F0-style Cortex-M0 memory map).
 * ELMO masks addresses, so ROM at 0x08000000 is where the .bin is loaded. */

MEMORY
{
    rom (rx)  : ORIGIN = 0x08000000, LENGTH = 64K
    ram (rwx) : ORIGIN = 0x20000000, LENGTH = 8K
}

ENTRY(reset_handler)

SECTIONS
{
    .text : {
        KEEP(*(.vectors))
        *(.text*)
        . = ALIGN(4);
        *(.rodata*)
        . = ALIGN(4);
    } >rom

    .preinit_array : { KEEP(*(.preinit_array)) } >rom
    .init_array    : { KEEP(*(SORT(.init_array.*))) KEEP(*(.init_array)) } >rom
    .fini_array    : { KEEP(*(.fini_array)) KEEP(*(SORT(.fini_array.*))) } >rom
    .ARM.extab     : { *(.ARM.extab*) } >rom
    .ARM.exidx     : { *(.ARM.exidx*) } >rom

    .data : {
        _data = .;
        *(.data*)
        . = ALIGN(4);
        _edata = .;
    } >ram AT >rom
    _data_loadaddr = LOADADDR(.data);

    .bss : {
        _bss = .;
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
    } >ram

    /DISCARD/ : { *(.eh_frame) }

    . = ALIGN(4);
    end = .;    /* start of the heap, used by malloc */
}

PROVIDE(_stack = ORIGIN(ram) + LENGTH(ram));
