"""Plot trace 1 of the Dumbo target (first Spongent round).

Needs data/dumbo/traces/ copied from external/ELMO/output/ after
`make run` in src/targets/dumbo.

Run (on Windows):  uv run analysis/plot_trace_dumbo.py
"""

import matplotlib.pyplot as plt
import numpy as np

from eitp60.traces import PROJECT_ROOT

path = PROJECT_ROOT / "data" / "dumbo" / "traces" / "trace00001.trc"
trace = np.loadtxt(path)

plt.figure(figsize=(12, 4))
plt.plot(trace, linewidth=0.5, color="black")
plt.xlim(0, len(trace) - 1)
plt.xlabel("Sample (clock cycle after starttrigger)")
plt.ylabel("Modelled power (ELMO, M0 model)")
plt.title(f"Dumbo, Spongent round 1: trace 1 ({len(trace)} samples)")
plt.tight_layout()

out = PROJECT_ROOT / "figures" / "dumbo_trace1.png"
plt.savefig(out, dpi=150)
print("Saved", out)
plt.show()
