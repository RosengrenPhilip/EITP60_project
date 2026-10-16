# Shared build rules for ELMO targets.
# A target's Makefile sets SRCS (and optionally BINARY), then includes this file.
#   make        build main.bin
#   make run    build, then simulate it with ELMO
#   make clean  remove build output

COMMON := $(dir $(lastword $(MAKEFILE_LIST)))
ELMO   := $(abspath $(COMMON)../../../external/ELMO)

BINARY ?= main

PREFIX  ?= arm-none-eabi
CC      := $(PREFIX)-gcc
OBJCOPY := $(PREFIX)-objcopy
OBJDUMP := $(PREFIX)-objdump

ARCH_FLAGS := -mthumb -mcpu=cortex-m0 -msoft-float

CFLAGS += -Os -g
CFLAGS += -Wall -Wextra -Wshadow -Wundef -Wstrict-prototypes -Wmissing-prototypes
CFLAGS += -fno-common -ffunction-sections -fdata-sections
CFLAGS += -I$(COMMON)

LDFLAGS += --static -nostartfiles -T$(COMMON)m0.ld
LDFLAGS += -Wl,-Map=$(BINARY).map -Wl,--gc-sections
LDLIBS  += -Wl,--start-group -lc -lgcc -lnosys -Wl,--end-group

COMMON_OBJS := $(COMMON)startup.o $(COMMON)elmoasmfunctions.o
OBJS        := $(SRCS:.c=.o) $(COMMON_OBJS)

all: $(BINARY).bin $(BINARY).list

$(BINARY).elf: $(OBJS) $(COMMON)m0.ld
	$(CC) $(ARCH_FLAGS) $(LDFLAGS) $(OBJS) $(LDLIBS) -o $@

$(BINARY).bin: $(BINARY).elf
	$(OBJCOPY) -Obinary $< $@

$(BINARY).list: $(BINARY).elf
	$(OBJDUMP) -S $< > $@

%.o: %.c
	$(CC) $(CFLAGS) $(ARCH_FLAGS) -MMD -c $< -o $@

%.o: %.s
	$(CC) $(ARCH_FLAGS) -c $< -o $@

# ELMO reads its config files relative to its own folder, so run it from there.
run: $(BINARY).bin
	cd $(ELMO) && ./elmo $(abspath $(BINARY).bin)

clean:
	rm -f $(SRCS:.c=.o) $(SRCS:.c=.d) $(BINARY).elf $(BINARY).bin $(BINARY).list $(BINARY).map

-include $(SRCS:.c=.d)

.PHONY: all run clean
