#!/usr/bin/env bash
# Install Ren'Py and run the demo project. Works on Raspberry Pi OS / Debian
# Trixie (apt) and macOS (Homebrew cask).
#
# Usage:
#   sudo bash setup-renpy.sh        # Linux: install via apt (needs sudo)
#        bash setup-renpy.sh        # macOS: install via brew (no sudo)
#        bash setup-renpy.sh run    # run the demo (any OS, no sudo)
#
# Why two install paths:
#   - Linux: official SDK is x86_64 only; Trixie's apt 'renpy' is built for
#     ARM64 and just works on a Pi3.
#   - macOS: easiest is the Homebrew cask, which drops the SDK under
#     /Applications/renpy-<version>/. No CLI symlink, so we locate
#     renpy.sh inside that directory ourselves.

set -euo pipefail

CMD="${1:-install}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEMO_DIR="${SCRIPT_DIR}/demo-renpy"
OS="$(uname -s)"

find_renpy_runner() {
  # Prints a runner command (path or program name) on success, exits 1 on
  # failure. Caller execs the result with the project path.
  if command -v renpy >/dev/null 2>&1; then
    echo "renpy"
    return 0
  fi
  if [[ "$OS" == "Darwin" ]]; then
    local sh
    sh="$(ls -td /Applications/renpy-*/renpy.sh 2>/dev/null | head -1 || true)"
    if [[ -n "$sh" && -x "$sh" ]]; then
      echo "$sh"
      return 0
    fi
  fi
  return 1
}

copy_korean_font() {
  # Copy a system Korean font into game/fonts/Korean.ttf so options.rpy can
  # reference it via a stable relative path. Ren'Py is flaky at loading
  # absolute system paths.
  local dest="${DEMO_DIR}/game/fonts/Korean.ttf"
  mkdir -p "$(dirname "$dest")"
  if [[ -f "$dest" ]]; then
    return 0
  fi
  local src=""
  case "$OS" in
    Darwin)
      src="/System/Library/Fonts/Supplemental/AppleGothic.ttf"
      ;;
    Linux)
      # Prefer Noto Sans KR if installed (single-face .otf); fall back to
      # the CJK collection.
      for cand in \
        /usr/share/fonts/opentype/noto/NotoSansKR-Regular.otf \
        /usr/share/fonts/truetype/nanum/NanumGothic.ttf \
        /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc
      do
        [[ -f "$cand" ]] && src="$cand" && break
      done
      ;;
  esac
  if [[ -z "$src" || ! -f "$src" ]]; then
    echo "WARN: no system Korean font found; demo will show tofu." >&2
    echo "      Linux: apt install fonts-noto-cjk fonts-nanum" >&2
    return 1
  fi
  cp "$src" "$dest"
  echo "Korean font copied: $src -> $dest"
}

install_linux() {
  if [[ $EUID -ne 0 ]]; then
    echo "Linux install needs root: sudo bash $0" >&2
    exit 1
  fi
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y --no-install-recommends renpy
  copy_korean_font || true
}

install_mac() {
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found. Install it from https://brew.sh and re-run, or" >&2
    echo "download the Ren'Py SDK manually from https://www.renpy.org" >&2
    exit 1
  fi
  if find_renpy_runner >/dev/null 2>&1; then
    echo "Ren'Py is already installed."
  else
    brew install --cask renpy
  fi
  # Brew casks for non-notarized SDKs land with com.apple.quarantine set,
  # which makes Gatekeeper refuse to load librenpython.dylib. Strip it.
  for d in /Applications/renpy-*; do
    [[ -d "$d" ]] && xattr -dr com.apple.quarantine "$d" 2>/dev/null || true
  done
  copy_korean_font || true
}

run_demo() {
  local runner
  if ! runner="$(find_renpy_runner)"; then
    echo "Ren'Py not installed. Run:  bash $0" >&2
    exit 1
  fi
  if [[ ! -d "$DEMO_DIR/game" ]]; then
    echo "Demo project not found at $DEMO_DIR" >&2
    exit 1
  fi
  echo "Launching: $runner $DEMO_DIR"
  exec "$runner" "$DEMO_DIR"
}

case "$CMD" in
  install)
    case "$OS" in
      Linux)  install_linux ;;
      Darwin) install_mac ;;
      *) echo "Unsupported OS: $OS" >&2; exit 1 ;;
    esac
    echo
    echo "Done. Run the demo with:"
    echo "   bash $0 run"
    ;;
  run)
    run_demo
    ;;
  *)
    echo "Usage: $0 [install|run]" >&2
    exit 2
    ;;
esac
