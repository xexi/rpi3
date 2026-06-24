# Grammar Tap — terminal edition

The same fill-in-the-blank English-grammar drill as `demo-grammar-typing`,
**rebuilt for the terminal** so it runs fast on a Raspberry Pi 3.

## Why drop pygame

The grammar game was already 100% textual (no audio, no images, no `assets/`).
The only thing pygame did was draw text and read keys — and on a Pi 3 it pays
for that with a **60 FPS render loop** that repaints a full 980×640 surface
every frame even when nothing changes, plus font rasterization, alpha
overlays, and SDL/X11 overhead. That's why it felt sluggish.

This version is **event-driven**: it blocks waiting for a line of input and
uses ~0% CPU when idle, then redraws one screen. That is exactly the
"text-based only" workload the Pi 3 is fast at. Adding content later is just
editing `items.py`; there is no engine tax to pay.

## What's shared vs. new

| File | Status |
|---|---|
| `items.py` | **reused verbatim** from the pygame demo (curriculum tree) |
| `progress.py` | **reused verbatim** (`progress.json` mastery store) |
| `main.py` | **new** — ANSI/terminal I/O instead of pygame |

The lesson logic is identical: PASS-1 diagnostic → self-assess summary →
weak-queue review rounds until every item is clean → mastered, with progress
saved to `progress.json` (gitignored, single local profile).

## Run it

```bash
bash setup.sh          # no pip installs — pure stdlib Python 3
```

No virtualenv, no dependencies. Needs only Python 3 and a UTF-8 terminal.

## Terminal & font (the one real requirement)

Korean must render, which is the *terminal's* job, not the app's. The repo
ships a helper that installs the candidate terminals, the CJK fonts, and the
per-terminal font config, then launches this game in each so you can compare:

```bash
sudo bash ../setup-terminals.sh        # install terminals + fonts + configs
bash ../setup-terminals.sh run foot    # try the fast Wayland pick
bash ../setup-terminals.sh run all     # open the game in every GUI terminal
```

Notes on the candidates (RPi OS Trixie is Wayland/labwc):

- **`foot`** — native-Wayland, lightest; the recommended fast pick. Font (with
  Korean fallback) lives in `~/.config/foot/foot.ini`.
- **`urxvt` (rxvt-unicode)** — X11, runs via Xwayland; very light. Needs the
  font set in `~/.Xresources` (the helper writes this):
  ```
  URxvt.font: xft:DejaVu Sans Mono:size=14,xft:Noto Sans Mono CJK KR:size=14
  ```
  then `xrdb -merge ~/.Xresources`. The comma adds the Korean font as a
  fallback for glyphs the main font lacks.
- **Terminator / Tilix / lxterminal** — heavier (GTK/VTE) but render Korean out
  of the box once a CJK font is installed (fontconfig handles the fallback).
- **tmux** — a multiplexer you run *inside* any of the above; ensure UTF-8
  (`tmux -u`).

Give the window at least ~70 columns so the centred sentences fit. (`setup-korean.sh`
is only needed to *type* Hangul system-wide — this game just *displays* it.)

## Controls (type-and-submit)

In a card you **type the missing word and press Enter**:

- correct on the first try → green, +10, auto-advances
- wrong → shows the answer; in review you get up to 5 tries before it reveals
- **Enter on an empty line** = "모르겠어요" (skip / don't know)
- **`?`** = show the Korean grammar tip for this card
- **`q`** = back to the menu (saves your progress)

At the menu, **type a number and Enter** to pick a unit (or the full
diagnostic); **`q`** quits.

## What changed from the pygame version

- "Hold Tab to peek the tip" → **`?` toggles the tip** (terminals can't detect
  key *release*).
- Per-keystroke green/red letters → **type the whole word, then Enter** (your
  chosen input mode). This also means the blank no longer leaks the answer's
  letter count, and the deferred `isn't` / `doesn't` / question-word units
  (which need spaces and apostrophes) are now trivial to add later.
- The fading flash overlay → a brief coloured confirmation frame.
