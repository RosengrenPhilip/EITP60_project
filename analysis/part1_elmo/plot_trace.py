"""Plot one ELMO trace file.

Usage:  uv run analysis/part1_elmo/plot_trace.py data/mbedaes/traces/trace00001.trc
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/mbedaes/traces/trace00001.trc")
trace = np.loadtxt(path)

plt.figure(figsize=(12, 4))
plt.plot(trace, linewidth=0.6, color="black")
plt.xlabel("Sample (clock cycle after starttrigger)")
plt.ylabel("Modelled power")
plt.title(f"{path.name} ({len(trace)} samples)")
plt.tight_layout()

out = Path("figures") / f"{path.stem}.png"
plt.savefig(out, dpi=150)
print("Saved", out)
plt.show()
