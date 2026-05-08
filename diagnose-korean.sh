#!/usr/bin/env bash
# Diagnose Korean / fcitx5 setup on Raspberry Pi OS (Trixie).
#
# Prints a checklist of what's installed, configured, and running, plus the
# most common red flags. Safe to run as the desktop user (no sudo needed for
# most checks; a few use sudo if available).
#
# Usage:  bash diagnose-korean.sh
# Or:     bash diagnose-korean.sh > korean-report.txt   (to share the output)

set -u

c_red()   { printf '\033[31m%s\033[0m' "$*"; }
c_green() { printf '\033[32m%s\033[0m' "$*"; }
c_yellow(){ printf '\033[33m%s\033[0m' "$*"; }
c_dim()   { printf '\033[2m%s\033[0m'  "$*"; }

PASS=0; WARN=0; FAIL=0
ok()   { echo "  $(c_green '[ ok ]') $*"; PASS=$((PASS+1)); }
warn() { echo "  $(c_yellow '[warn]') $*"; WARN=$((WARN+1)); }
bad()  { echo "  $(c_red   '[FAIL]') $*"; FAIL=$((FAIL+1)); }
info() { echo "  $(c_dim   '[info]') $*"; }

section() { echo; echo "=== $* ==="; }

# ---------- 1. system ----------
section "1. System"
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  info "OS: ${PRETTY_NAME:-?}  (codename: ${VERSION_CODENAME:-?})"
  case "${VERSION_CODENAME:-}" in
    trixie|bookworm) ok "supported Debian release";;
    *) warn "untested release — package names may differ";;
  esac
fi
info "session type: ${XDG_SESSION_TYPE:-unset}    desktop: ${XDG_CURRENT_DESKTOP:-unset}"
if [[ "${XDG_SESSION_TYPE:-}" == "wayland" ]]; then
  ok "Wayland session (correct for labwc on RPi OS Trixie)"
elif [[ "${XDG_SESSION_TYPE:-}" == "x11" ]]; then
  warn "X11 session — fcitx5 still works, but Wayland is the RPi OS default"
fi

# ---------- 2. locale ----------
section "2. Locale"
if locale -a 2>/dev/null | grep -qi 'ko_KR\.utf'; then
  ok "ko_KR.UTF-8 locale is generated"
else
  bad "ko_KR.UTF-8 locale is NOT generated — run: sudo locale-gen ko_KR.UTF-8"
fi
info "current LANG=${LANG:-unset}   LC_ALL=${LC_ALL:-unset}"

# ---------- 3. fonts ----------
section "3. Fonts"
for pkg in fonts-noto-cjk fonts-nanum; do
  if dpkg -s "$pkg" >/dev/null 2>&1; then
    ok "$pkg installed"
  else
    bad "$pkg missing — Korean text will render as tofu (□□□)"
  fi
done
if command -v fc-list >/dev/null 2>&1; then
  cjk_count=$(fc-list :lang=ko 2>/dev/null | wc -l)
  if [[ "$cjk_count" -gt 0 ]]; then
    ok "fontconfig sees $cjk_count Korean-capable fonts"
  else
    bad "fontconfig sees 0 Korean fonts (cache may need: fc-cache -fv)"
  fi
fi

# ---------- 4. fcitx5 packages ----------
section "4. fcitx5 packages"
required=(fcitx5 fcitx5-hangul)
for pkg in "${required[@]}"; do
  if dpkg -s "$pkg" >/dev/null 2>&1; then
    ok "$pkg installed"
  else
    bad "$pkg NOT installed — Hangul cannot compose without it"
  fi
done
optional=(fcitx5-config-qt fcitx5-frontend-gtk3 fcitx5-frontend-gtk4 fcitx5-frontend-qt5 fcitx5-frontend-qt6)
for pkg in "${optional[@]}"; do
  if dpkg -s "$pkg" >/dev/null 2>&1; then
    ok "$pkg installed"
  else
    warn "$pkg not installed (apps using that toolkit may not get fcitx)"
  fi
done

# Common red flag: legacy fcitx4 / ibus still around.
for pkg in fcitx fcitx-hangul ibus ibus-hangul nimf nabi; do
  if dpkg -s "$pkg" >/dev/null 2>&1; then
    warn "legacy '$pkg' is installed — can conflict with fcitx5; consider:  sudo apt purge $pkg"
  fi
done

# ---------- 5. fcitx5 process ----------
section "5. fcitx5 runtime"
if pgrep -x fcitx5 >/dev/null 2>&1; then
  ok "fcitx5 is running (pid $(pgrep -x fcitx5 | tr '\n' ' '))"
else
  bad "fcitx5 is NOT running — try:  fcitx5 -d   (or log out and back in)"
fi
if command -v gdbus >/dev/null 2>&1; then
  if gdbus call --session --dest org.freedesktop.DBus --object-path /org/freedesktop/DBus \
       --method org.freedesktop.DBus.ListNames 2>/dev/null | grep -q 'org.fcitx.Fcitx5'; then
    ok "fcitx5 DBus service is registered"
  else
    warn "fcitx5 DBus service not visible (apps won't connect)"
  fi
fi

# ---------- 6. env vars ----------
section "6. Input-method env vars"
expected_vars=(GTK_IM_MODULE QT_IM_MODULE XMODIFIERS)
for v in "${expected_vars[@]}"; do
  cur="${!v:-}"
  if [[ "$v" == "XMODIFIERS" ]]; then
    [[ "$cur" == "@im=fcitx" ]] && ok "$v=$cur" || bad "$v='$cur' (expected '@im=fcitx')"
  else
    [[ "$cur" == "fcitx" ]] && ok "$v=$cur" || bad "$v='$cur' (expected 'fcitx')"
  fi
done
if [[ -r /etc/environment ]]; then
  if grep -q '^GTK_IM_MODULE=fcitx' /etc/environment; then
    ok "/etc/environment has GTK_IM_MODULE=fcitx"
  else
    warn "/etc/environment is missing IM vars — they won't survive reboot"
  fi
fi
if [[ -n "${GTK_IM_MODULE:-}" && "${GTK_IM_MODULE}" != "fcitx" ]]; then
  bad "GTK_IM_MODULE is set in your shell to '$GTK_IM_MODULE' — log out and back in to pick up /etc/environment"
fi

# ---------- 7. keyboard layout ----------
section "7. XKB keyboard layout"
if [[ -r /etc/default/keyboard ]]; then
  layout=$(awk -F= '/^XKBLAYOUT/{gsub(/"/,"",$2); print $2}' /etc/default/keyboard)
  variant=$(awk -F= '/^XKBVARIANT/{gsub(/"/,"",$2); print $2}' /etc/default/keyboard)
  info "/etc/default/keyboard: XKBLAYOUT='$layout' XKBVARIANT='$variant'"
  if [[ "$layout" == "kr" ]]; then
    ok "system layout is Korean"
    [[ "$variant" == "kr104" ]] || warn "variant is '$variant' — kr104 is the usual choice for 한/영+한자 keys"
  else
    warn "system layout is '$layout' — 한/영 key won't be recognized"
  fi
fi
if command -v localectl >/dev/null 2>&1; then
  echo "  localectl status:"
  localectl status 2>/dev/null | sed 's/^/    /'
fi
# Active session layout (Wayland-aware fallback)
if command -v setxkbmap >/dev/null 2>&1 && [[ "${XDG_SESSION_TYPE:-}" == "x11" ]]; then
  echo "  setxkbmap -query:"
  setxkbmap -query 2>/dev/null | sed 's/^/    /'
fi

# ---------- 8. fcitx5 user config ----------
section "8. fcitx5 user config"
PROFILE="${HOME}/.config/fcitx5/profile"
if [[ -f "$PROFILE" ]]; then
  ok "profile exists: $PROFILE"
  imname=$(awk -F= '/^DefaultIM/{print $2}' "$PROFILE" | tr -d ' ')
  if [[ "$imname" == "hangul" ]]; then
    ok "DefaultIM=hangul"
  else
    warn "DefaultIM='$imname' (expected 'hangul') — fix in fcitx5-config-qt"
  fi
  if grep -q '^Name=keyboard-kr' "$PROFILE"; then
    ok "profile uses keyboard-kr layout"
  elif grep -q '^Name=keyboard-us' "$PROFILE"; then
    warn "profile uses keyboard-us — fcitx5 will override system kr layout to us"
  fi
else
  bad "no fcitx5 profile at $PROFILE — run: fcitx5 -d  then  fcitx5-config-qt"
fi
AUTOSTART="${HOME}/.config/autostart/fcitx5.desktop"
if [[ -f "$AUTOSTART" ]]; then
  ok "autostart entry present"
else
  warn "no autostart entry — fcitx5 won't start at login"
fi

# ---------- 9. fcitx5-diagnose ----------
section "9. fcitx5-diagnose (truncated)"
if command -v fcitx5-diagnose >/dev/null 2>&1; then
  # Show just the headline issues — full output is huge.
  fcitx5-diagnose 2>/dev/null \
    | grep -E '^(##|\* |Error|Warning)' \
    | head -n 30 \
    | sed 's/^/  /' \
    || warn "fcitx5-diagnose ran but produced no output"
  info "for the full report:  fcitx5-diagnose | less"
else
  warn "fcitx5-diagnose not found (install fcitx5 package)"
fi

# ---------- summary ----------
section "Summary"
echo "  $(c_green   "passed: $PASS")    $(c_yellow "warnings: $WARN")    $(c_red "failures: $FAIL")"
if [[ $FAIL -gt 0 ]]; then
  echo
  echo "Common fixes:"
  echo "  - Hangul not composing in Chromium: log out + back in (env vars take effect on session start)"
  echo "  - 한/영 key does nothing:             check section 7 (XKBLAYOUT) and section 8 (keyboard-kr)"
  echo "  - Korean text shows as boxes:         sudo apt install fonts-noto-cjk fonts-nanum && fc-cache -fv"
  echo "  - fcitx5 won't autostart:             ls ~/.config/autostart/fcitx5.desktop, then reboot"
  exit 1
fi
exit 0
