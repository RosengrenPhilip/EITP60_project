"""Sanity check of the whole pipeline: recover the template target's key with CPA.

Build and simulate first (in WSL):  cd src/targets/template && make run
then copy external/ELMO/output/{traces,randdata.txt,printdata.txt} to
data/template/ (each ELMO run overwrites output/).
Then run (on Windows):              uv run analysis/cpa_template.py
"""

import matplotlib.pyplot as plt
import numpy as np

from eitp60.cpa import HW, correlate, rank_guesses
from eitp60.traces import PROJECT_ROOT, load_inputs, load_traces

# Same S-box as src/targets/template/main.c, generated from its definition
# (multiplicative inverse in GF(2^8) followed by an affine map).
def _make_sbox() -> np.ndarray:
    inv = [0] * 256
    for a in range(1, 256):
        for b in range(1, 256):
            p, x, y = 0, a, b
            while y:
                if y & 1:
                    p ^= x
                x = ((x << 1) ^ 0x11B) if x & 0x80 else x << 1
                y >>= 1
            if p == 1:
                inv[a] = b
                break
    rot = lambda v, n: ((v << n) | (v >> (8 - n))) & 0xFF
    return np.array([v ^ rot(v, 1) ^ rot(v, 2) ^ rot(v, 3) ^ rot(v, 4) ^ 0x63 for v in inv], dtype=np.uint8)


SBOX = _make_sbox()

DATA = PROJECT_ROOT / "data" / "template"
traces = load_traces(DATA)
inputs = load_inputs(output_dir=DATA)
print(f"{traces.shape[0]} traces, {traces.shape[1]} samples each")

guesses = np.arange(256, dtype=np.uint8)
recovered = []
for byte in range(inputs.shape[1]):
    # Leakage model: Hamming weight of the S-box output for every key guess.
    hypotheses = HW[SBOX[inputs[:, byte, None] ^ guesses]].astype(float)
    corr = correlate(hypotheses, traces)
    recovered.append(rank_guesses(corr)[0])
    if byte == 0:
        corr_byte0 = corr

print("Recovered key:", bytes(recovered).hex())

best = rank_guesses(corr_byte0)[0]
plt.plot(np.abs(corr_byte0).T, color="lightgray", linewidth=0.5)
plt.plot(np.abs(corr_byte0[best]), color="tab:red", label=f"best guess 0x{best:02x}")
plt.xlabel("Sample (cycle)")
plt.ylabel("|correlation|")
plt.title("CPA on key byte 0 (template target)")
plt.legend()
out = PROJECT_ROOT / "figures" / "cpa_template.png"
plt.savefig(out, dpi=150)
print("Saved", out)
