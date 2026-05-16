#!/usr/bin/env bash
# Korean (Hangul) support for Raspberry Pi OS 64-bit (Trixie / Debian 13,
# Wayland + labwc compositor — the current default as of 2026).
#
# Why this script exists: even the "ko" locale image ships without a working
# Hangul input method. The old fcitx4 / ibus / nabi recipes you'll find on
# Korean blogs do NOT work cleanly on labwc/Wayland; fcitx5 is the only stack
# that implements the Wayland input-method protocol completely enough for
# Chromium, GTK4, and Qt apps to receive composed Hangul.
#
# What this does:
#   1. Generates the ko_KR.UTF-8 locale (UI language stays as-is).
#   2. Installs CJK + Nanum fonts so Korean text renders everywhere.
#   3. Installs fcitx5 + fcitx5-hangul + GTK/Qt frontends.
#   4. Wires GTK_IM_MODULE / QT_IM_MODULE / XMODIFIERS via /etc/environment.
#   5. Sets system XKB layout to kr/kr104 (physical Korean keyboard with
#      dedicated 한/영 and 한자 keys).
#   6. Autostarts fcitx5 on login and pre-seeds a kr + Hangul profile that
#      matches the system layout.
#
# Files modified (backups suffixed .bak.YYYYMMDDHHMMSS):
#   /etc/locale.gen
#   /etc/environment
#   /etc/default/keyboard
#
# Usage:  sudo bash setup-korean.sh
# After it finishes: reboot, then press 한/영 (or Ctrl+Space) to toggle.
# If something seems off, run:  bash diagnose-korean.sh

set -euo pipefail

CURRENT_STEP="(starting up)"
on_error() {
  local exit_code=$?
  echo >&2
  echo "===========================================================" >&2
  echo "FAILED during step: ${CURRENT_STEP}" >&2
  echo "  at line ${BASH_LINENO[0]} (exit code ${exit_code})" >&2
  echo "  command: ${BASH_COMMAND}" >&2
  echo >&2
  echo "Run  bash diagnose-korean.sh  to inspect current state." >&2
  echo "===========================================================" >&2
  exit "$exit_code"
}
trap on_error ERR

ts() { date +%Y%m%d%H%M%S; }
backup_once() {
  # Backup a file the first time we touch it in this run.
  local f="$1"
  if [[ -f "$f" && ! -f "${f}.bak."* ]] 2>/dev/null; then
    cp -a "$f" "${f}.bak.$(ts)"
  fi
}

# ---------- pre-flight ----------
CURRENT_STEP="pre-flight checks"

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo bash $0" >&2
  exit 1
fi

REAL_USER="${SUDO_USER:-}"
if [[ -z "$REAL_USER" || "$REAL_USER" == "root" ]]; then
  echo "Refusing to run: this script needs the desktop user's home dir" >&2
  echo "for fcitx5 autostart and profile. Run via:" >&2
  echo "   sudo bash $0          (from a normal user shell)" >&2
  exit 1
fi
REAL_HOME="$(getent passwd "$REAL_USER" | cut -d: -f6 || true)"
if [[ -z "$REAL_HOME" || ! -d "$REAL_HOME" ]]; then
  echo "Cannot resolve home directory for user '$REAL_USER'." >&2
  exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
  echo "apt-get not found — this script targets Debian/Raspberry Pi OS." >&2
  exit 1
fi

# Soft check the release; warn but don't abort, since package names are stable
# across recent Debian.
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  case "${VERSION_CODENAME:-}" in
    trixie|bookworm) ;;
    *) echo "WARN: untested release '${VERSION_CODENAME:-unknown}'. Proceeding anyway." >&2 ;;
  esac
fi

# ---------- 1. locale ----------
CURRENT_STEP="1/6 generate ko_KR.UTF-8 locale"
echo "==> ${CURRENT_STEP}"
backup_once /etc/locale.gen
if grep -qE '^[# ]*ko_KR\.UTF-8 UTF-8' /etc/locale.gen; then
  sed -i 's/^# *\(ko_KR\.UTF-8 UTF-8\)/\1/' /etc/locale.gen
else
  # Some minimal images don't ship the line at all.
  echo 'ko_KR.UTF-8 UTF-8' >> /etc/locale.gen
fi
locale-gen ko_KR.UTF-8

# ---------- 2. fonts ----------
CURRENT_STEP="2/6 install Korean fonts"
echo "==> ${CURRENT_STEP}"
export DEBIAN_FRONTEND=noninteractive
apt-get update
# Required: these are what actually make Korean text render. Fail loudly.
apt-get install -y --no-install-recommends \
  fonts-noto-cjk \
  fonts-nanum
# Optional extras: large CJK glyph set and the Nanum monospace coding font.
# fonts-nanum-coding was dropped in Debian Trixie (folded into fonts-nanum),
# and fonts-noto-cjk-extra is just a bigger glyph set — neither is needed for
# Korean to render, so install best-effort and don't abort if absent.
for pkg in fonts-noto-cjk-extra fonts-nanum-coding; do
  if ! apt-get install -y --no-install-recommends "$pkg" 2>/dev/null; then
    echo "WARN: optional font package '$pkg' not installed (skipping)" >&2
  fi
done

# ---------- 3. fcitx5 ----------
CURRENT_STEP="3/6 install fcitx5 + Hangul engine"
echo "==> ${CURRENT_STEP}"
# Required core: fail loudly if any of these are missing.
apt-get install -y --no-install-recommends \
  fcitx5 \
  fcitx5-hangul \
  fcitx5-config-qt \
  fcitx5-frontend-gtk3
# Optional frontends: best-effort so a missing Qt6/GTK4 package on an exotic
# mirror doesn't abort the whole setup. We log what didn't install.
for pkg in fcitx5-frontend-gtk4 fcitx5-frontend-qt5 fcitx5-frontend-qt6; do
  if ! apt-get install -y --no-install-recommends "$pkg" 2>/dev/null; then
    echo "WARN: optional package '$pkg' not installed (skipping)" >&2
  fi
done

# ---------- 4. IM env vars ----------
CURRENT_STEP="4/6 wire input-method env vars"
echo "==> ${CURRENT_STEP}"
ENV_FILE=/etc/environment
backup_once "$ENV_FILE"
declare -A IM_VARS=(
  [GTK_IM_MODULE]=fcitx
  [QT_IM_MODULE]=fcitx
  [XMODIFIERS]="@im=fcitx"
  [SDL_IM_MODULE]=fcitx
  [GLFW_IM_MODULE]=ibus  # GLFW only knows "ibus"; fcitx5 implements that protocol.
)
for k in "${!IM_VARS[@]}"; do
  v="${IM_VARS[$k]}"
  if grep -q "^${k}=" "$ENV_FILE"; then
    sed -i "s|^${k}=.*|${k}=${v}|" "$ENV_FILE"
  else
    echo "${k}=${v}" >> "$ENV_FILE"
  fi
done

# ---------- 5. XKB layout ----------
CURRENT_STEP="5/6 set system XKB layout to kr/kr104"
echo "==> ${CURRENT_STEP}"
# /etc/default/keyboard is what labwc/Wayland and the console both read at
# session start. setxkbmap won't help on Wayland — this file is the source
# of truth.
backup_once /etc/default/keyboard
cat > /etc/default/keyboard <<'EOF'
XKBMODEL="pc105"
XKBLAYOUT="kr"
XKBVARIANT="kr104"
XKBOPTIONS=""
BACKSPACE="guess"
EOF
if command -v setupcon >/dev/null 2>&1; then
  # setupcon can fail on headless / no-console systems; that's fine.
  setupcon --force --save 2>/dev/null || \
    echo "INFO: setupcon could not apply to console (harmless on headless)." >&2
fi

# ---------- 6. autostart + fcitx5 profile ----------
CURRENT_STEP="6/6 enable fcitx5 autostart and seed profile"
echo "==> ${CURRENT_STEP} (user: ${REAL_USER})"
AUTOSTART_DIR="${REAL_HOME}/.config/autostart"
sudo -u "$REAL_USER" mkdir -p "$AUTOSTART_DIR"
cat > "${AUTOSTART_DIR}/fcitx5.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=Fcitx 5
Exec=fcitx5
Icon=fcitx
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
chown -R "$REAL_USER:$REAL_USER" "${REAL_HOME}/.config"

PROFILE_DIR="${REAL_HOME}/.config/fcitx5"
sudo -u "$REAL_USER" mkdir -p "$PROFILE_DIR"
PROFILE="${PROFILE_DIR}/profile"
if [[ ! -f "$PROFILE" ]]; then
  cat > "$PROFILE" <<'EOF'
[Groups/0]
Name=Default
Default Layout=kr
DefaultIM=hangul

[Groups/0/Items/0]
Name=keyboard-kr
Layout=kr
Variant=kr104

[Groups/0/Items/1]
Name=hangul
Layout=

[GroupOrder]
0=Default
EOF
  chown "$REAL_USER:$REAL_USER" "$PROFILE"
else
  echo "INFO: existing fcitx5 profile preserved at $PROFILE" >&2
fi

CURRENT_STEP="(done)"
echo
echo "Done. Reboot now:  sudo reboot"
echo "After reboot, press 한/영 (or Ctrl+Space) to toggle English / 한글."
echo "If something looks off:  bash diagnose-korean.sh"
