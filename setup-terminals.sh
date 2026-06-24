#!/usr/bin/env bash
# setup-terminals.sh — install candidate terminal emulators + Korean fonts and
# launch the Grammar Tap terminal demo (demo-grammar-tui) in each, so you can
# feel which one is smoothest on the Raspberry Pi 3.
#
# Raspberry Pi OS Trixie defaults to Wayland/labwc (see setup-korean.sh). On
# that stack the candidates rank roughly:
#   * foot        native Wayland, lightest — the recommended "fast" pick.
#   * urxvt       X11; runs via Xwayland. Light and classic.
#   * terminator  GTK3, Wayland-native; heavier, feature-rich.
#   * tilix       GTK3/VTE, Wayland-native; heavier.
#   * lxterminal  the LXDE default; usually already installed.
#   * tmux        a multiplexer you run *inside* any of the above.
#
# Korean rendering is the terminal's job. GTK terminals (terminator/tilix/
# lxterminal) get it for free from fontconfig once the CJK fonts are installed;
# foot and urxvt take an explicit "Latin mono + Korean mono fallback" font,
# which this script writes into their configs and also passes on the command
# line when launching. (This only makes the game's Korean *display*; to *type*
# Hangul system-wide, run setup-korean.sh.)
#
# Usage:
#   sudo bash setup-terminals.sh          install all terminals + fonts + configs
#   bash setup-terminals.sh list          show which are installed + how to launch
#   bash setup-terminals.sh run <name>    launch the game in one terminal
#   bash setup-terminals.sh run all       launch it in every installed GUI terminal
#     <name> = foot | urxvt | terminator | tilix | lxterminal | tmux

set -uo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
GAME_DIR="${REPO}/demo-grammar-tui"
LAUNCHER="${TMPDIR:-/tmp}/grammar-tap-launch.sh"

# Latin monospace primary + Korean monospace fallback. Both font packages are
# installed below; "Noto Sans Mono CJK KR" is monospaced and lines up with the
# double-width Hangul in a terminal grid.
PRIMARY="DejaVu Sans Mono"
KOFB="Noto Sans Mono CJK KR"
SIZE=14

CANDIDATES=(foot urxvt terminator tilix lxterminal tmux)
pkg_of() { case "$1" in
  foot) echo foot ;; urxvt) echo rxvt-unicode ;; terminator) echo terminator ;;
  tilix) echo tilix ;; lxterminal) echo lxterminal ;; tmux) echo tmux ;;
esac; }
bin_of() { case "$1" in urxvt) echo urxvt ;; *) echo "$1" ;; esac; }

c_g(){ printf '\033[32m%s\033[0m' "$*"; }
c_y(){ printf '\033[33m%s\033[0m' "$*"; }
c_d(){ printf '\033[2m%s\033[0m'  "$*"; }
ok()   { echo "  $(c_g '[ ok ]') $*"; }
warn() { echo "  $(c_y '[warn]') $*"; }

usage() {
  cat <<EOF
Usage:
  sudo bash $0          install all terminals + fonts + configs
  bash $0 list          show which are installed + how to launch
  bash $0 run <name>    launch the game in one terminal
  bash $0 run all       launch it in every installed GUI terminal
    <name> = foot | urxvt | terminator | tilix | lxterminal | tmux
EOF
}

# ---------- install ----------

do_install() {
  if [[ $EUID -ne 0 ]]; then
    echo "Installing needs root. Run:  sudo bash $0" >&2
    exit 1
  fi
  local real_user real_home
  real_user="${SUDO_USER:-}"
  if [[ -z "$real_user" || "$real_user" == root ]]; then
    echo "Run via 'sudo bash $0' from your normal user (need your \$HOME for configs)." >&2
    exit 1
  fi
  real_home="$(getent passwd "$real_user" | cut -d: -f6)"

  export DEBIAN_FRONTEND=noninteractive
  echo "==> apt update"
  apt-get update || warn "apt update had problems (continuing)"

  echo "==> Korean fonts (required for the game to render Hangul)"
  apt-get install -y --no-install-recommends fonts-noto-cjk fonts-nanum \
    || warn "font install had problems — Korean may show as tofu (□□□)"

  echo "==> helpers (xrdb for urxvt resources; xwayland so X11 urxvt runs on labwc)"
  for p in x11-xserver-utils xwayland; do
    apt-get install -y --no-install-recommends "$p" 2>/dev/null && ok "$p" || warn "$p unavailable (skipping)"
  done

  echo "==> terminal emulators (best-effort each)"
  for t in "${CANDIDATES[@]}"; do
    local p; p="$(pkg_of "$t")"
    if apt-get install -y --no-install-recommends "$p" 2>/dev/null; then ok "$p"; else warn "$p not available on this mirror (skipping)"; fi
  done

  fc-cache -f >/dev/null 2>&1 || true
  configure_user "$real_user" "$real_home"

  echo
  echo "Done. Now, as your normal user (not sudo):"
  echo "    bash $0 list           # see what installed"
  echo "    bash $0 run foot       # try the fast Wayland pick"
  echo "    bash $0 run all        # open the game in every GUI terminal at once"
}

# Write per-user font configs for the two terminals that need them, owned by
# the real user even though we run as root.
configure_user() {
  local user="$1" home="$2"

  # urxvt — ~/.Xresources font line (replace any existing URxvt.font).
  local xres="$home/.Xresources"
  touch "$xres"
  grep -v '^URxvt\.font:' "$xres" 2>/dev/null > "$xres.tmp" || true
  mv "$xres.tmp" "$xres"
  printf 'URxvt.font: xft:%s:size=%s,xft:%s:size=%s\n' "$PRIMARY" "$SIZE" "$KOFB" "$SIZE" >> "$xres"
  chown "$user:$user" "$xres"
  ok "wrote $xres"

  # foot — ~/.config/foot/foot.ini (only if it doesn't already carry our line).
  local footdir="$home/.config/foot" foot
  foot="$footdir/foot.ini"
  mkdir -p "$footdir"
  if [[ ! -f "$foot" ]] || ! grep -q 'Grammar Tap' "$foot"; then
    cat > "$foot" <<EOF
# Grammar Tap — Latin mono + Korean mono fallback
[main]
font=${PRIMARY}:size=${SIZE}, ${KOFB}:size=${SIZE}
EOF
    ok "wrote $foot"
  else
    warn "kept existing $foot (already configured)"
  fi
  chown -R "$user:$user" "$footdir"

  # Merge the new resources into a running X/Xwayland session if there is one.
  if command -v xrdb >/dev/null 2>&1 && [[ -n "${DISPLAY:-}" ]]; then
    sudo -u "$user" DISPLAY="$DISPLAY" xrdb -merge "$xres" 2>/dev/null || true
  fi
}

# ---------- launch ----------

make_launcher() {
  cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
# Generated by setup-terminals.sh — runs the game, then waits so the window
# doesn't vanish when you quit.
cd "${GAME_DIR}" || { echo "missing ${GAME_DIR}"; read -rsn1; exit 1; }
bash setup.sh
echo
echo "── 게임 종료 · press any key to close ──"
read -rsn1
EOF
  chmod +x "$LAUNCHER"
}

launch_one() {
  local t="$1" bin; bin="$(bin_of "$t")"
  if ! command -v "$bin" >/dev/null 2>&1; then
    warn "$t not installed (sudo apt install $(pkg_of "$t"))"
    return 1
  fi
  make_launcher
  case "$t" in
    foot)       foot --font="${PRIMARY}:size=${SIZE},${KOFB}:size=${SIZE}" bash "$LAUNCHER" ;;
    urxvt)      urxvt -fn "xft:${PRIMARY}:size=${SIZE},xft:${KOFB}:size=${SIZE}" -e bash "$LAUNCHER" ;;
    terminator) terminator -x bash "$LAUNCHER" ;;
    tilix)      tilix -e "bash $LAUNCHER" ;;
    lxterminal) lxterminal -e "bash $LAUNCHER" ;;
    tmux)       tmux new-session "bash $LAUNCHER" ;;
  esac
}

do_run() {
  if [[ $EUID -eq 0 ]]; then
    echo "Run 'run' as your normal user, not root — a GUI terminal needs your session." >&2
    exit 1
  fi
  local name="${1:-}"
  if [[ -z "$name" ]]; then echo "which terminal? e.g.  bash $0 run foot"; usage; exit 1; fi

  if [[ "$name" != tmux && -z "${WAYLAND_DISPLAY:-}${DISPLAY:-}" ]]; then
    echo "No graphical session (WAYLAND_DISPLAY/DISPLAY unset) — GUI terminals can't open."
    echo "Run this from the Pi desktop, or test in-place with:  bash $0 run tmux"
    exit 1
  fi

  if [[ "$name" == all ]]; then
    for t in foot urxvt terminator tilix lxterminal; do
      command -v "$(bin_of "$t")" >/dev/null 2>&1 || continue
      echo "launching $t ..."
      ( launch_one "$t" >/dev/null 2>&1 & )
    done
    echo "(tmux runs inline — try it with:  bash $0 run tmux)"
  else
    launch_one "$name"
  fi
}

# ---------- list ----------

do_list() {
  echo "candidate terminals:"
  for t in "${CANDIDATES[@]}"; do
    if command -v "$(bin_of "$t")" >/dev/null 2>&1; then
      printf '  %s %-11s %s\n' "$(c_g '✓')" "$t" "$(c_d "bash $0 run $t")"
    else
      printf '  %s %-11s %s\n' "$(c_y '✗')" "$t" "$(c_d "sudo apt install $(pkg_of "$t")")"
    fi
  done
  echo
  if command -v fc-list >/dev/null 2>&1; then
    local n; n="$(fc-list :lang=ko 2>/dev/null | wc -l)"
    echo "Korean-capable fonts visible to fontconfig: $n"
    [[ "$n" -gt 0 ]] || echo "  none yet — run:  sudo bash $0"
  fi
}

# ---------- dispatch ----------

case "${1:-install}" in
  install)        do_install ;;
  list|ls)        do_list ;;
  run)            shift; do_run "${1:-}" ;;
  -h|--help|help) usage ;;
  *) echo "unknown command: $1" >&2; usage; exit 1 ;;
esac
