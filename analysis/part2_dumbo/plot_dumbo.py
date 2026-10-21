"""
All CPA figures for the dumbo target (Part 2: reproduction and extension).
uv run analysis/part2_dumbo/plot_dumbo.py
"""

import matplotlib.pyplot as plt
import numpy as np

from cpa_dumbo import attack, load
from eitp60.cpa import rank_guesses
from eitp60.traces import PROJECT_ROOT

DATA = PROJECT_ROOT / "data" / "dumbo"
CSV = PROJECT_ROOT / "results" / "success_rate_dumbo.csv"
FIGURES = PROJECT_ROOT / "figures"

# Noise figures
SIGMA = 6
N_TRACES = 200  # all traces
SEED = 0
ZOOM = (780, 1000)

# Read by from Fig. 3 ("0 errors") from paper
PAPER_TRACES = np.arange(25, 41)
PAPER_RATE = np.array([0.22, 0.375, 0.43, 0.59, 0.615, 0.735, 0.775, 0.82,
                       0.88, 0.85, 0.905, 0.89, 0.925, 0.96, 0.915, 0.93])


def save(name, **kwargs):
    out = FIGURES / name
    plt.savefig(out, dpi=150, **kwargs)
    print("Saved", out)
    plt.close()


def plot_cpa(corr_byte1, title, name):
    """|correlation| of every guess for mask byte 1, best guess in red."""
    best = rank_guesses(corr_byte1)[0]
    plt.figure()
    plt.plot(np.abs(corr_byte1).T, color="lightgray", linewidth=0.5)
    plt.plot(np.abs(corr_byte1[best]), color="tab:red", label=f"best guess 0x{best:02x}")
    plt.xlim(0, 3000)
    plt.xlabel("Sample (cycle)")
    plt.ylabel("|correlation|")
    plt.title(title)
    plt.legend()
    save(name)


def plot_residual(corr_noisy, corr_clean, true):
    # negative = noise lowered the correlation, positive = noise raised it
    residual = np.abs(corr_noisy) - np.abs(corr_clean)
    plt.figure()
    plt.plot(residual.T, color="lightgray", linewidth=0.5)
    plt.plot(residual[true], color="tab:red", label=f"correct guess 0x{true:02x}")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.xlim(0, 3000)
    plt.xlabel("Sample (cycle)")
    plt.ylabel("|correlation| (σ = %g) − |correlation| (σ = 0)" % SIGMA)
    plt.title(f"Effect of noise on CPA, mask in AD1 (dumbo), {N_TRACES} traces")
    plt.legend()
    save(f"cpa_dumbo_residual_sigma{SIGMA}.png")


def plot_noise_comparison(corr_noisy, corr_clean, true):
    """Correct guess with and without noise in the same plot, zoomed in."""
    plt.figure()
    plt.plot(np.abs(corr_clean[true]), color="tab:blue", linewidth=1, label="σ = 0")
    plt.plot(np.abs(corr_noisy[true]), color="tab:red", linewidth=1, label=f"σ = {SIGMA}")
    plt.xlim(*ZOOM)
    plt.xlabel("Sample (cycle)")
    plt.ylabel("|correlation|")
    plt.title(f"CPA on mask in AD1 (dumbo), correct guess 0x{true:02x}, {N_TRACES} traces")
    plt.legend(title="Noise std")
    save(f"cpa_dumbo_compare_sigma{SIGMA}.png")


def plot_success_rate(csv_path=CSV, n_repetitions=200, min_traces=10):
    data = np.loadtxt(csv_path, delimiter=",", skiprows=1)
    data = data[data[:, 1] >= min_traces]

    plt.figure()
    for sigma in np.unique(data[:, 0]):
        rows = data[data[:, 0] == sigma]
        plt.plot(rows[:, 1], rows[:, 2], marker="o", markersize=4, label=f"σ = {sigma:g}")

    plt.ylim(0, 1.05)
    plt.xlabel("Number of traces")
    plt.ylabel("Success rate (full mask)")
    plt.title(f"CPA on dumbo mask, {n_repetitions} repetitions, no error recovery")
    # Outside the axes so it doesn't cover the curves
    plt.legend(title="Noise std", loc="center left", bbox_to_anchor=(1.02, 0.5))
    save("success_rate_dumbo.png", bbox_inches="tight")


def plot_paper_comparison(csv_path=CSV):
    """Our simulated success rates (ELMO, Cortex-M0) next to the paper's measured
    ones."""
    data = np.loadtxt(csv_path, delimiter=",", skiprows=1)
    data = data[data[:, 1] >= PAPER_TRACES[0]]

    print("RMS difference to the paper per noise level:")
    plt.figure()
    for sigma in np.unique(data[:, 0]):
        rows = data[data[:, 0] == sigma]
        rms = np.sqrt(np.mean((rows[:, 2] - PAPER_RATE) ** 2))
        print(f"  sigma = {sigma:g}: {rms:.3f}")
        plt.plot(rows[:, 1], rows[:, 2], marker="o", markersize=3, linewidth=1, alpha=0.6,
                 label=f"ELMO M0, σ = {sigma:g}")
    plt.plot(PAPER_TRACES, PAPER_RATE, color="black", marker="s", markersize=4, linewidth=2,
             linestyle="--", label="Paper, real M4")

    plt.ylim(0, 1.05)
    plt.xlabel("Number of traces")
    plt.ylabel("Success rate (full mask)")
    plt.title("Simulated Cortex-M0 vs measured Cortex-M4, no error recovery")
    plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
    save("compare_paper_dumbo.png", bbox_inches="tight")


if __name__ == "__main__":
    traces, ad, mask = load(DATA)
    true = mask[1]

    # same traces with and without noise, so the only difference is the noise
    rng = np.random.default_rng(SEED)
    idx = rng.choice(len(traces), size=N_TRACES, replace=False)
    noisy = traces[idx] + rng.normal(0, SIGMA, size=(N_TRACES, traces.shape[1]))
    recovered_clean, corr_clean = attack(traces[idx], ad[idx])
    recovered_noisy, corr_noisy = attack(noisy, ad[idx])

    print("True mask:            ", bytes(mask).hex())
    print("Recovered, no noise:  ", bytes(recovered_clean).hex())
    print(f"Recovered, sigma {SIGMA}:   ", bytes(recovered_noisy).hex())

    plot_cpa(corr_clean, "CPA on mask in AD1 (dumbo)", "cpa_dumbo.png")
    plot_cpa(corr_noisy, f"CPA on mask in AD1 (dumbo), σ = {SIGMA}, {N_TRACES} traces",
             f"cpa_dumbo_sigma{SIGMA}.png")
    plot_residual(corr_noisy, corr_clean, true)
    plot_noise_comparison(corr_noisy, corr_clean, true)
    plot_success_rate()
    plot_paper_comparison()
