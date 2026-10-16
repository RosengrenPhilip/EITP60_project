# EITP60 project: power side-channel analysis with ELMO

Course project for EITP60 (Hardware Hacking and Side-Channel Security).
The assignment is in [resources/project.pdf](resources/project.pdf), and the
ELMO manual is in [resources/ELMODocumentation.pdf](resources/ELMODocumentation.pdf).

## Layout

| Path | Contents |
| --- | --- |
| `external/ELMO/` | Upstream ELMO simulator, a git submodule pinned to a fixed commit (unmodified) |
| `src/` | Our target C/assembly code and the Python package `eitp60` |
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

## Running ELMO

ELMO reads its config (`elmodefines.h`) and coefficient file relative to the
current directory, so it is run from `external/ELMO`:

```bash
cd external/ELMO
./elmo path/to/target.bin
```

Traces are written to `external/ELMO/output/traces/`.

## Upstream code

| Component | Source | Commit |
| --- | --- | --- |
| ELMO | https://github.com/bristol-sca/ELMO | `7c4e2930714a498d08a1b4469acc262f58952fb8` |
