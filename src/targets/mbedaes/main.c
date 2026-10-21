// MBedAES target: ELMO's Examples/DPATraces/MBedAES, built with our common
// startup code and ELMO helpers instead of the prebuilt elmoasmfunctions.o
// shipped upstream, which current arm-none-eabi-ld refuses to link.
//
// 200 traces, key 00 01 02 ... 0f, random plaintexts (see MBedAES.c).

#include "../../../external/ELMO/Examples/DPATraces/MBedAES/MBedAES.c"
