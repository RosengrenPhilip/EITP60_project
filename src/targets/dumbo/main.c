// Dumbo (Elephant-160) target: first Spongent round of the first permuted
// associated-data block, as attacked in Vialar, "Trumping the Elephant", 2022.
//
// In Elephant, AD block 0 (nonce || AD[0..7]) only initialises the tag; the
// first block that goes through Spongent is AD block 1 (AD[8..27]), XORed
// with mask = lfsr_step(P(key || 0^32)) (see encrypt.c). Here AD block 1 is
// chosen at random for each trace and only round 1 is inside the triggers.
//
// Output (output/printdata.txt), 20 bytes per line group:
//   first 20 bytes:  the mask (the CPA target, printed once for checking)
//   then per trace:  the state after round 1
// Input (output/randdata.txt): the 20 AD-block bytes of each trace.
//
// Author code (unmodified): spongent.c, encrypt.c, elephant_160.h from the
// NIST LWC Elephant submission. This file is ours.

#include <string.h>

#include "elephant_160.h"
#include "elmoasmfunctionsdef.h"

#define NOTRACES 200
#define KEYBYTES 16

// Helpers defined in spongent.c but not declared in elephant_160.h.
extern int sBoxLayer[256];
void pLayer(BYTE *state);
BYTE retnuoCl(BYTE lfsr);

static const BYTE key[KEYBYTES] = {
    0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
    0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
};

// Round constant of Spongent-pi[160] in round 1 (lfsrIV in spongent.c).
#define ROUND1_IV 0x75

// Round 1 of permutation() in spongent.c, which always runs all 80 rounds.
static void spongent_round1(BYTE *state)
{
    state[0] ^= ROUND1_IV;
    state[BLOCK_SIZE - 1] ^= retnuoCl(ROUND1_IV);
    for (int j = 0; j < BLOCK_SIZE; j++) {
        state[j] = sBoxLayer[state[j]];
    }
    pLayer(state);
}

int main(void)
{
    BYTE expanded_key[BLOCK_SIZE] = {0};
    BYTE mask[BLOCK_SIZE];
    BYTE state[BLOCK_SIZE];

    // Same key schedule as crypto_aead_impl() in encrypt.c.
    memcpy(expanded_key, key, KEYBYTES);
    permutation(expanded_key);
    lfsr_step(mask, expanded_key);

    for (int i = 0; i < BLOCK_SIZE; i++) {
        printbyte(&mask[i]);
    }

    for (int t = 0; t < NOTRACES; t++) {
        for (int i = 0; i < BLOCK_SIZE; i++) {
            randbyte(&state[i]);
            state[i] ^= mask[i];
        }

        starttrigger();
        spongent_round1(state);
        endtrigger();

        for (int i = 0; i < BLOCK_SIZE; i++) {
            printbyte(&state[i]);
        }
    }

    endprogram();
    return 0;
}
