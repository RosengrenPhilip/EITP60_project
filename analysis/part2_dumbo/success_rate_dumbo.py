"""Success rate of the CPA in cpa_dumbo.py versus number of traces.

As in the paper: run the attack once for each number of traces, then repeat
that N_REPETITIONS times. No error recovery.

Reproduced: sigma 0 with 25-40 traces (the paper's Fig. 3, "0 errors").
Extension:  fewer traces (down to 5) and added Gaussian noise (sigma 1-6).

    uv run analysis/part2_dumbo/success_rate_dumbo.py
"""

import csv

import numpy as np

from cpa_dumbo import attack, load
from eitp60.traces import PROJECT_ROOT
from plot_dumbo import plot_success_rate

N_REPETITIONS = 200
TRACE_COUNTS = range(5, 41)  # as in the paper
SEED = 0
# Gaussian noise std in ELMO units.
SIGMAS = [0, 1, 2, 3, 4, 5, 6]
traces, ad, mask = load(PROJECT_ROOT / "data" / "dumbo")

rows = []
for sigma_index, sigma in enumerate(SIGMAS):
    # ine generator per noise level, so each noise level gets the same
    # random numbers no matter which other levels are run
    rng = np.random.default_rng([SEED, sigma_index])
    successes = np.zeros(len(TRACE_COUNTS))
    for rep in range(N_REPETITIONS):
        for i, n in enumerate(TRACE_COUNTS):
            idx = rng.choice(len(traces), size=n, replace=False)
            noisy = traces[idx] + rng.normal(0, sigma, size=(n, traces.shape[1]))
            recovered, _ = attack(noisy, ad[idx])
            successes[i] += np.array_equal(recovered, mask)
        if (rep + 1) % 10 == 0:
            print(f"sigma {sigma}: {rep + 1}/{N_REPETITIONS} repetitions done", flush=True)


    
    print(f"\nnoise std = {sigma}")
    for n, s in zip(TRACE_COUNTS, successes):
        print(f"{n} traces: success rate {s / N_REPETITIONS:.3f}")
        rows.append((sigma, n, s / N_REPETITIONS))

out_csv = PROJECT_ROOT / "results" / "success_rate_dumbo.csv"
out_csv.parent.mkdir(exist_ok=True)
with open(out_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["sigma", "n_traces", "success_rate"])
    writer.writerows(rows)
print("Saved", out_csv)

plot_success_rate(out_csv, n_repetitions=N_REPETITIONS)
