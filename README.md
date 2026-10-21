# eitp60: power side-channel analysis with elmo

cpa on elephant-dumbo (vialar, "trumping the elephant", sstic 2022) with elmo
traces instead of physical measurements. assignment: [resources/project.pdf](resources/project.pdf).

elmo and the arm toolchain run in wsl (ubuntu). the python analysis runs on
windows. all commands are run from the project root.

we used UV to easly fix dependencies. commands to install in setup

## setup

```bash
# windows, administrator powershell, then reboot
wsl --install -d Ubuntu

# wsl: arm toolchain, submodules and elmo
git submodule update --init
bash scripts/setup_wsl.sh

# windows: install uv (once), then the python environment
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv sync
```

## part 1: elmo validation on the mbedaes example

```bash
# wsl: build, simulate, copy the output
make -C src/targets/mbedaes run
mkdir -p data/mbedaes
cp -r external/ELMO/output/traces external/ELMO/output/randdata.txt \
      external/ELMO/output/asmoutput/asmtrace00001.txt data/mbedaes/
```

```powershell
# windows
uv run analysis/part1_elmo/plot_trace.py data/mbedaes/traces/trace00001.trc  # figures/trace00001.png
uv run analysis/part1_elmo/trigger_region_mbedaes.py                         # figures/mbedaes_trace_rounds.png
uv run analysis/part1_elmo/cpa_mbedaes.py                                    # figures/cpa_MBedAes.png
```

## part 2: dumbo

```bash
# wsl: build, simulate, copy the output
make -C src/targets/dumbo run
mkdir -p data/dumbo
cp -r external/ELMO/output/traces external/ELMO/output/randdata.txt \
      external/ELMO/output/printdata.txt data/dumbo/
```

```powershell
# windows
uv run analysis/part2_dumbo/cpa_dumbo.py            # prints recovered and true mask
uv run analysis/part2_dumbo/plot_trace_dumbo.py     # figures/dumbo_trace1.png
uv run analysis/part2_dumbo/success_rate_dumbo.py   # results/success_rate_dumbo.csv (slow, see below)
uv run analysis/part2_dumbo/plot_dumbo.py           # all other dumbo figures
```

`success_rate_dumbo.py` runs 200 repetitions for 5-40 traces and noise
σ = 0-6, which takes about 40 hours.
## reproducibility

- elmo inputs: `main.c` reads each input byte with `randbyte()`, which elmo
  answers with `rand()` and logs to `randdata.txt`. the number of traces is
  `NOTRACES` (200) in `main.c`.
- elmo configuration: unmodified defaults, `external/ELMO/elmodefines.h` and
  the cortex-m0 leakage model in `external/ELMO/coeffs.txt`.
- the traces (about 120 mb) are not in git. `data/dumbo/randdata.txt` and
  `data/dumbo/printdata.txt` from the run used in the report are.
- a new elmo run may draw different random inputs, so results can differ
  slightly from the report.
- the analysis uses fixed seeds (`SEED = 0`), so with the same traces the
  numbers are identical.

## upstream code and our changes

everything in `external/` is unmodified upstream code:

- `external/ELMO/`: https://github.com/bristol-sca/ELMO, commit `7c4e2930714a498d08a1b4469acc262f58952fb8`
- `external/nist-lwc-power-analysis/`: https://github.com/kudelskisecurity/nist-lwc-power-analysis, commit `6bc4573aacae1ab86c9b769792be5c1c86e7e144`
- `external/elephant/`: nist lwc elephant submission, source in `external/elephant/SOURCE.md`

everything else is written by us, except `src/targets/common/elmoasmfunctions*`,
which is copied from elmo (we added `.thumb_func` to the `.s` file so it links).
