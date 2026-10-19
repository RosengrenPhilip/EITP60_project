"""Correlation Power Analysis helpers (independent of the target algorithm)."""

import numpy as np

# Hamming weight of every byte value
HW = np.array([bin(x).count("1") for x in range(256)], dtype=np.uint8)


def correlate(hypotheses: np.ndarray, traces: np.ndarray) -> np.ndarray:
    """pearson coeff for each hypothesis with every trace sample

    hypotheses: (n_traces, n_guesses) predicted leakage per key guess
    traces:     (n_traces, n_samples)
    returns:    (n_guesses, n_samples)
    """
    h = hypotheses - hypotheses.mean(axis=0)
    t = traces - traces.mean(axis=0)
    num = h.T @ t
    denom = np.outer(np.sqrt((h**2).sum(axis=0)), np.sqrt((t**2).sum(axis=0)))
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.nan_to_num(num / denom)


def rank_guesses(correlation: np.ndarray) -> np.ndarray:    
    """Key guesses sorted from most to least likely (by peak |correlation|)."""
    return np.argsort(-np.abs(correlation).max(axis=1))
