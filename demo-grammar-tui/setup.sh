#!/usr/bin/env bash
# Grammar Tap — terminal edition. No game engine, no pip installs: this is
# pure-stdlib Python, so "setup" just makes sure we run under UTF-8 and
# launches the app. The heavy lifting (Korean fonts) is the terminal's job —
# see README.md. setup-korean.sh in the repo root installs the Nanum/Noto
# fonts these terminals fall back to.

set -euo pipefail

cd "$(dirname "$0")"

# Force UTF-8 so Korean glyphs and box characters render regardless of the
# inherited locale (urxvt/tmux usually set this already; belt and braces).
export PYTHONUTF8=1
export PYTHONIOENCODING=UTF-8

exec python3 main.py
