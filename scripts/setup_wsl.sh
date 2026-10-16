#!/usr/bin/env bash
# One-time setup inside WSL (Ubuntu): installs the host and ARM toolchains,
# then builds ELMO from the external/ELMO submodule.
# Run from the project root:  bash scripts/setup_wsl.sh
set -euo pipefail

cd "$(dirname "$0")/.."

sudo apt-get update
sudo apt-get install -y build-essential gcc-arm-none-eabi libnewlib-arm-none-eabi

git submodule update --init external/ELMO

# -B forces a rebuild: the repo ships a prebuilt Linux binary we don't trust.
make -B -C external/ELMO

gcc --version | head -n1
arm-none-eabi-gcc --version | head -n1
echo "ELMO built at external/ELMO/elmo"
