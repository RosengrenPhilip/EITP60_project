"""Load ELMO output (power traces, inputs and outputs) into numpy arrays."""

from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ELMO_OUTPUT = PROJECT_ROOT / "external" / "ELMO" / "output"


def load_traces(output_dir: Path = ELMO_OUTPUT) -> np.ndarray:
    """Return all traces as an array of shape (n_traces, n_samples).

    ELMO writes one text file per trace (trace00001.trc, ...) with one
    power value per line.
    """
    files = sorted((output_dir / "traces").glob("trace*.trc"))
    if not files:
        raise FileNotFoundError(f"No traces found in {output_dir / 'traces'}")
    return np.stack([np.loadtxt(f) for f in files])


def _load_hex_bytes(path: Path, block_size: int) -> np.ndarray:
    values = [int(line, 16) for line in path.read_text().split()]
    return np.array(values, dtype=np.uint8).reshape(-1, block_size)


def load_inputs(block_size: int = 16, output_dir: Path = ELMO_OUTPUT) -> np.ndarray:
    """Bytes the target read with randbyte(), shape (n_traces, block_size)."""
    return _load_hex_bytes(output_dir / "randdata.txt", block_size)


def load_outputs(block_size: int = 16, output_dir: Path = ELMO_OUTPUT) -> np.ndarray:
    """Bytes the target wrote with printbyte(), shape (n_traces, block_size)."""
    return _load_hex_bytes(output_dir / "printdata.txt", block_size)
