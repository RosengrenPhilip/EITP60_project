"""Test Vector Leakage Assessment (fixed-vs-random Welch t-test)."""

import numpy as np

# Usual pass/fail threshold: |t| > 4.5 at any sample indicates leakage.
THRESHOLD = 4.5


def welch_t(group_a: np.ndarray, group_b: np.ndarray) -> np.ndarray:
    """Welch's t-statistic per sample for two sets of traces (n_traces, n_samples)."""
    mean_a, mean_b = group_a.mean(axis=0), group_b.mean(axis=0)
    var_a, var_b = group_a.var(axis=0, ddof=1), group_b.var(axis=0, ddof=1)
    denom = np.sqrt(var_a / len(group_a) + var_b / len(group_b))
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (mean_a - mean_b) / denom
    # Samples with zero variance in both groups carry no information.
    return np.nan_to_num(t, nan=0.0, posinf=0.0, neginf=0.0)
