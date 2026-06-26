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

Korean must render, which is the *terminal's* job, not the app's. Install the
CJK fonts once with the repo's Korean helper — it installs the same Noto/Nanum
faces the terminals fall back to (and, as a bonus, system-wide Hangul *input*):

```bash
sudo bash ../setup-korean.sh        # installs fonts-noto-cjk + fonts-nanum
```

That gives you the monospaced **Noto Sans Mono CJK KR** face that lines up with
the double-width Hangul in a terminal grid. Then pick a terminal (RPi OS Trixie
is Wayland/labwc):

- **`foot`** — native-Wayland, lightest; the recommended fast pick. Set the
  font (with Korean fallback) in `~/.config/foot/foot.ini`:
  ```
  [main]
  font=DejaVu Sans Mono:size=14, Noto Sans Mono CJK KR:size=14
  ```
- **`urxvt` (rxvt-unicode)** — X11, runs via Xwayland; very light. Set the font
  in `~/.Xresources`:
  ```
  URxvt.font: xft:DejaVu Sans Mono:size=14,xft:Noto Sans Mono CJK KR:size=14
  ```
  then `xrdb -merge ~/.Xresources`. The comma adds the Korean font as a
  fallback for glyphs the main font lacks.
- **Terminator / Tilix / lxterminal** — heavier (GTK/VTE) but render Korean out
  of the box once a CJK font is installed (fontconfig handles the fallback).
- **tmux** — a multiplexer you run *inside* any of the above; ensure UTF-8
  (`tmux -u`).

Give the window at least ~70 columns so the centred sentences fit.

## Controls (type-and-submit)

In a card you **type the missing word and press Enter**:

- correct on the first try → green, +10, auto-advances
- wrong → try again; you get up to **3 tries** before the answer is revealed
- **type at least one character** — a bare Enter does nothing (no skip)
- **`?`** = show the Korean grammar tip for this card
- **`q`** = back to the menu (saves your progress; the only way to leave a card
  unmastered)

At the menu, **type a number and Enter** to pick a unit (small subject);
**`q`** quits.

## What changed from the pygame version

- "Hold Tab to peek the tip" → **`?` toggles the tip** (terminals can't detect
  key *release*).
- Per-keystroke green/red letters → **type the whole word, then Enter** (your
  chosen input mode). This also means the blank no longer leaks the answer's
  letter count, and the deferred `isn't` / `doesn't` / question-word units
  (which need spaces and apostrophes) are now trivial to add later.
- The fading flash overlay → a brief coloured confirmation frame.
