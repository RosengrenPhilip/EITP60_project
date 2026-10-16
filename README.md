# EITP60 project: power side-channel analysis with ELMO

Course project for EITP60 (Hardware Hacking and Side-Channel Security).
The assignment is in [resources/project.pdf](resources/project.pdf), and the
ELMO manual is in [resources/ELMODocumentation.pdf](resources/ELMODocumentation.pdf).

## Layout

| Path | Contents |
| --- | --- |
| `external/ELMO/` | Upstream ELMO simulator, a git submodule pinned to a fixed commit (unmodified) |
| `src/targets/` | Target C/assembly code that ELMO simulates, one folder per target |
| `src/targets/common/` | Shared startup code, linker script, ELMO helper functions and build rules |
| `src/eitp60/` | Python package: trace loading, TVLA, CPA |
| `analysis/` | Analysis scripts and notebooks (TVLA, CPA, ...) |
| `figures/` | Generated figures for the report |
| `scripts/` | Setup and build helpers |
| `resources/` | Assignment and documentation PDFs |

## Setup

ELMO and the ARM toolchain run in WSL (Ubuntu). The Python analysis runs
on Windows or in WSL through uv.

1. Install WSL once from an **administrator** PowerShell, then reboot:
   ```powershell
   wsl --install -d Ubuntu
   ```
2. Inside Ubuntu, from this folder (`/mnt/c/Users/<you>/Documents/EITP60/project`):
   ```bash
   bash scripts/setup_wsl.sh
   ```
   This installs `build-essential` and `gcc-arm-none-eabi`, then builds `external/ELMO/elmo`.
3. Install the Python environment:
   ```bash
   uv sync
   ```

When you clone this repo fresh, also run `git submodule update --init`.

## Building and running a target

Each target lives in its own folder under `src/targets/`. To start a new one,
copy `src/targets/template/` and edit `main.c` (add more `.c` files to `SRCS`
in its `Makefile`). In WSL:

```bash
cd src/targets/template
make        # build main.bin
make run    # build, then simulate with ELMO
```

ELMO writes traces to `external/ELMO/output/traces/`, the inputs read with
`randbyte()` to `output/randdata.txt` and the bytes printed with
`printbyte()` to `output/printdata.txt`. Load them in Python with
`eitp60.traces`. Then, on Windows:

```powershell
uv run analysis/cpa_template.py   # sanity check: recovers the template's key
```

## Upstream code

| Component | Source | Commit |
| --- | --- | --- |
| ELMO | https://github.com/bristol-sca/ELMO | `7c4e2930714a498d08a1b4469acc262f58952fb8` |
