#!/usr/bin/env bash
# Install pygame-ce in a venv and run the grammar typing game.
# No audio: this demo is text-only by design (see HANDOFF.md).
# Korean fonts come from setup-korean.sh (Nanum / Noto CJK).

set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install pygame-ce

python main.py
