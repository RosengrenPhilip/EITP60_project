"""Identify the code region between the triggers in the MBedAES traces (Part 1, task 3).

Needs data/mbedaes/ with traces/ and asmtrace00001.txt copied from
external/ELMO/output/ after running Examples/DPATraces/MBedAES in ELMO.

Run (on Windows):  uv run analysis/trigger_region_mbedaes.py

ELMO's asmtrace00001.txt logs the instructions of trace 1, one line per
trace sample (cycle). Mapping each sample to its instruction address and the
function it belongs to (from MBedAES.list) shows what the trace covers. The
AES rounds are found by how often their code runs: rounds are loop
iterations, so their instructions are executed several times, while the
first key addition and the final round run once.
"""

import re
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

from eitp60.traces import PROJECT_ROOT, load_traces

DATA = PROJECT_ROOT / "data" / "mbedaes"
LISTING = PROJECT_ROOT / "external/ELMO/Examples/DPATraces/MBedAES/MBedAES.list"
ENCRYPT = "mbedtls_aes_encrypt"


def function_ranges(listing):
    """(start, end, name) for every function in an objdump listing."""
    starts = [
        (int(m.group(1), 16), m.group(2))
        for m in re.finditer(r"^([0-9a-f]{8}) <(\w+)>:", listing.read_text(), re.M)
    ]
    return [(a, b, name) for (a, name), (b, _) in zip(starts, starts[1:] + [(2**32, "")])]


def sample_addresses(asmtrace):
    """Instruction address for every trace sample.

    The first line of the log is the tail of the store that turned the
    trigger on (its start was printed before the file was opened), and the
    last line is the store that turns it off; neither is a trace sample.
    Continuation lines (register lists of push/pop) keep the previous address.
    """
    addresses, current = [], None
    for line in asmtrace.read_text().splitlines()[1:-1]:
        m = re.match(r"--- 0x([0-9A-F]+):", line)
        if m:
            current = int(m.group(1), 16)
        addresses.append(current)
    return addresses


def function_of(address, ranges):
    return next((name for a, b, name in ranges if a <= address < b), "?")


traces = load_traces(DATA)
addresses = sample_addresses(DATA / "asmtrace00001.txt")
ranges = function_ranges(LISTING)
assert len(addresses) == traces.shape[1], "asmtrace does not match the traces"

functions = [function_of(a, ranges) for a in addresses]
in_encrypt = [i for i, f in enumerate(functions) if f == ENCRYPT]
enc_start, enc_end = in_encrypt[0], in_encrypt[-1]

# How many times each instruction inside the encryption is entered.
visits = Counter()
for i in range(enc_start, enc_end + 1):
    if i == enc_start or addresses[i] != addresses[i - 1]:
        visits[addresses[i]] += 1

# Split the encryption into runs of code with the same visit count.
segments = []
for i in range(enc_start, enc_end + 1):
    k = visits[addresses[i]]
    if segments and segments[-1][0] == k:
        segments[-1][2] = i
    else:
        segments.append([k, i, i])
# Drop tiny runs (loop counter, branches) by merging them into the previous one.
merged = []
for k, s, e in segments:
    if merged and e - s < 4:
        merged[-1][2] = e
    else:
        merged.append([k, s, e])

labels = ["Round 0: load input + AddRoundKey"]
labels += [f"Round {r}" for r in range(1, len(merged) - 1)]
labels += [f"Round {len(merged) - 1} (final) + store output"]

print(f"{traces.shape[0]} traces, {traces.shape[1]} samples (cycles) each\n")
print(f"Samples 0-{enc_start - 1}: {', '.join(dict.fromkeys(functions[:enc_start]))} (trigger + call overhead)")
for label, (k, s, e) in zip(labels, merged):
    print(f"Samples {s}-{e} ({e - s + 1} cycles): {label}")
print(f"Samples {enc_end + 1}-{len(addresses) - 1}: {', '.join(dict.fromkeys(functions[enc_end + 1:]))} (return + trigger)")

# Plot trace 1 with the regions marked.
fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(traces[0], linewidth=0.6, color="black")
for n, (k, s, e) in enumerate(merged):
    ax.axvspan(s, e, color="tab:blue" if n % 2 else "tab:orange", alpha=0.15, linewidth=0)
    ax.text((s + e) / 2, 1.01, "R0" if n == 0 else f"R{n}", transform=ax.get_xaxis_transform(),
            ha="center", va="bottom", fontsize=8)
ax.set_xlim(0, traces.shape[1] - 1)
ax.set_xlabel("Sample (clock cycle after starttrigger)")
ax.set_ylabel("Modelled power (ELMO, M0 model)")
ax.set_title("MBedAES trace 1: region between the triggers = mbedtls_aes_encrypt", pad=18)
fig.tight_layout()
out = PROJECT_ROOT / "figures" / "mbedaes_trace_rounds.png"
fig.savefig(out, dpi=150)
print("\nSaved", out)
