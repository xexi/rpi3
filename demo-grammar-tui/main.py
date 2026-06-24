#!/usr/bin/env python3
"""Grammar Tap — terminal edition.

A fill-in-the-blank English-grammar drill for Korean kids, rebuilt to run
*fast* on a Raspberry Pi 3. No game engine: it blocks on line input and uses
~0% CPU when idle, instead of pygame's 60 FPS repaint of a full surface.

Same lesson logic as the pygame demo (curriculum tree, weak-queue mastery
loop, progress.json) — only the I/O layer changed:

  * Output : ANSI colours + a cleared screen, width-aware so double-wide
             Korean centres correctly.
  * Input  : type the word, press Enter (cooked line input — handles
             backspace for free, no raw/termios mode).

Run inside a UTF-8 terminal with a Korean-capable font (urxvt is lightest;
Terminator / Tilix / lxterminal+tmux all work). See README.md.
"""

import os
import random
import shutil
import sys
import time
from unicodedata import east_asian_width

import progress
from items import CURRICULUM, iter_units

# Mastery loop tuning — mirrors the pygame build.
MAX_TRIES = 5          # wrong submissions in a review showing before the answer is revealed
ADVANCE_PAUSE = 0.45   # seconds to admire a correct answer before the next card

# ---- ANSI ------------------------------------------------------------------

ESC = "\x1b["
RESET = ESC + "0m"
BOLD = ESC + "1m"


def fg(code):
    return f"{ESC}38;5;{code}m"


# Palette echoes the pygame colours (256-colour; fine on any X terminal).
INK = fg(252)        # default sentence text
HINT = fg(209)       # Korean meaning gloss
TYPED = fg(78)       # correct / locked green
TARGET = fg(75)      # the blank / accents
DIM = fg(244)        # cues, footer hints
DANGER = fg(203)     # wrong
SECTION = fg(180)    # section headers
GOLD = fg(220)

BADGE = {            # menu mastery dots
    "untouched": f"{DIM}○{RESET}",
    "started":   f"{fg(214)}◐{RESET}",
    "mastered":  f"{TYPED}●{RESET}",
}


def _enable_windows_ansi():
    """Turn on VT processing so colours work in a Windows dev console."""
    if os.name != "nt":
        return
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetConsoleMode(k.GetStdHandle(-11), 7)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass


# ---- width-aware layout ----------------------------------------------------


def cwidth(s):
    """Display columns of *s*, counting CJK as 2 (ignores ANSI-free text only)."""
    return sum(2 if east_asian_width(ch) in ("W", "F") else 1 for ch in s)


def term_size():
    sz = shutil.get_terminal_size((80, 24))
    return sz.columns, sz.lines


def pad_center(visible_width):
    cols, _ = term_size()
    return " " * max(0, (cols - visible_width) // 2)


def clear():
    sys.stdout.write(ESC + "2J" + ESC + "H")


def writeln(s=""):
    sys.stdout.write(s + "\n")


def center_plain(s, color=""):
    """Centre a single colour-free string."""
    return pad_center(cwidth(s)) + color + s + (RESET if color else "")


# ---- card / curriculum helpers ---------------------------------------------


def build_cards(units):
    cards = []
    for unit in units:
        for idx, (before, answer, after, korean, cue) in enumerate(unit["items"]):
            cards.append({
                "unit_id": unit["id"], "idx": idx,
                "before": before, "answer": answer, "after": after,
                "korean": korean, "cue": cue,
                "tip": unit["tip"], "unit_title_ko": unit["title_ko"],
            })
    return cards


def sentence_line(card, fill=None, fill_color=TARGET):
    """Build the (visible_text, colored_text) for one card's sentence.

    fill=None  -> show a blank ("____").
    fill=text  -> show that text where the blank was, in fill_color.
    """
    blank = "____"
    parts = []  # (text, color)
    if card["before"]:
        parts.append((card["before"], INK))
    if fill is None:
        parts.append((blank, TARGET))
    else:
        parts.append((fill, fill_color))
    if card["cue"]:
        parts.append((f" ({card['cue']})", DIM))
    if card["after"]:
        parts.append((card["after"], INK))

    visible = "".join(t for t, _ in parts)
    colored = "".join(c + t + RESET for t, c in parts)
    return visible, colored


# ---- input -----------------------------------------------------------------

class ToMenu(Exception):
    """Raised from a prompt to bail back to the topic menu."""


def read_line(prompt):
    """Blocking line input. '' = skip, 'q' = menu, '?' = toggle tip."""
    try:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        return input()
    except (EOFError, KeyboardInterrupt):
        raise ToMenu()


# ---- the game --------------------------------------------------------------

class Game:
    def __init__(self):
        self.progress = progress.load()
        self.score = 0
        self.units = []
        self.cards = None       # set while a run is in progress (for partial save)
        self.cleared = {}

    # ---- menu --------------------------------------------------------------

    def menu_rows(self):
        rows = [{"kind": "diagnostic"}]
        for section in CURRICULUM:
            rows.append({"kind": "section", "section": section})
            for unit in section["units"]:
                rows.append({"kind": "unit", "unit": unit})
        return rows

    def run(self):
        _enable_windows_ansi()
        while True:
            rows = self.menu_rows()
            try:
                units = self.draw_menu(rows)   # chosen unit list, or None to quit
            except ToMenu:
                units = None
            if units is None:
                clear()
                writeln(center_plain("안녕! 또 만나요 👋", HINT))
                writeln()
                return
            try:
                self.play(units)
            except ToMenu:
                self.save()                    # persist partial weak-queue progress
            self.cards = None

    def draw_menu(self, rows):
        # Build a numbered, selectable list (typing the number picks it).
        choices = []  # parallel list of selectable row dicts
        clear()
        writeln()
        writeln(center_plain("Grammar Tap", BOLD + TARGET))
        writeln(center_plain("주제를 골라 연습해요 · 틀린 문제는 다시 풀어요", HINT))
        writeln()
        n = 0
        for row in rows:
            if row["kind"] == "section":
                s = row["section"]
                writeln(f"   {SECTION}{BOLD}{s['section']}. {s['title_en']}  ·  {s['title_ko']}{RESET}")
            elif row["kind"] == "diagnostic":
                n += 1
                choices.append(row)
                writeln(f"   {GOLD}{n:>2}{RESET}  {TARGET}▶ 전체 진단 (모든 단원){RESET}")
            else:
                n += 1
                choices.append(row)
                u = row["unit"]
                badge = BADGE[progress.badge_for(self.progress, u["id"])]
                writeln(f"   {GOLD}{n:>2}{RESET}  {badge}  {u['title_en']}  ·  {DIM}{u['title_ko']}{RESET}")
        writeln()
        writeln(center_plain("번호를 입력하고 Enter · q 나가기", DIM))
        writeln()

        while True:
            ans = read_line("  골라보세요 ▶ ").strip().lower()
            if ans in ("q", "quit", "exit"):
                return None
            if ans.isdigit() and 1 <= int(ans) <= len(choices):
                row = choices[int(ans) - 1]
                if row["kind"] == "diagnostic":
                    return [u for _, u in iter_units()]
                return [row["unit"]]
            # anything else: re-prompt without redrawing the whole menu

    # ---- a full run over a set of units ------------------------------------

    def play(self, units):
        self.units = units
        self.cards = cards = build_cards(units)
        self.cleared = cleared = {(c["unit_id"], c["idx"]): False for c in cards}

        # PASS 1 — diagnostic: each card once, single attempt.
        for i, card in enumerate(cards):
            ok = self.ask_card(card, position=(i + 1, len(cards)), review=False)
            cleared[(card["unit_id"], card["idx"])] = ok

        weak = [c for c in cards if not cleared[(c["unit_id"], c["idx"])]]
        if not weak:
            self.mastered(cleared)
            self.save()
            return

        self.summary(cards, weak, units)

        # REVIEW — re-serve only weak items, reshuffled each round, until the
        # queue drains. A card leaves the queue when typed clean (first try)
        # or skipped; a dirty/revealed pass keeps it for the next round.
        queue = list(weak)
        while queue:
            round_list = list(queue)
            random.shuffle(round_list)
            for card in round_list:
                outcome = self.review_card(card, left=len(queue))
                if outcome in ("clean", "skip"):
                    queue.remove(card)
                    if outcome == "clean":
                        cleared[(card["unit_id"], card["idx"])] = True

        self.mastered(cleared)
        self.save()

    # ---- a single card -----------------------------------------------------

    def card_header(self, card, position=None, left=None, review=False):
        cols, rows = term_size()
        clear()
        for _ in range(max(1, rows // 2 - 7)):
            writeln()

        mode = f"{TARGET}복습{RESET}" if review else f"{INK}학습{RESET}"
        if review:
            counter = f"{DIM}남은 {left}개{RESET}"
        else:
            counter = f"{DIM}{position[0]} / {position[1]}{RESET}"
        bar = f"{mode}   {DIM}{card['unit_title_ko']}{RESET}"
        score = f"{GOLD}점수 {self.score}{RESET}"
        # left bar, centred counter, right score — laid out on one row
        pad = max(1, (cols - cwidth(_strip(bar)) - cwidth(_strip(score))) // 2 - 6)
        writeln(f"  {bar}{' ' * pad}{counter}{' ' * pad}{score}")
        writeln()
        writeln(center_plain(card["korean"], HINT + BOLD))
        writeln()

    def ask_card(self, card, position, review):
        """PASS-1 card: one attempt. Returns True if clean (correct first try)."""
        show_tip = False
        while True:
            self.card_header(card, position=position, review=review)
            self._draw_blank(card, show_tip)
            ans = read_line(center_plain("입력 ▶ ", TARGET))
            cmd = self._command(ans, card)
            if cmd == "tip":
                show_tip = True
                continue
            if cmd == "skip":
                self._reveal(card)
                return False
            if cmd == "answer":
                if ans.strip().lower() == card["answer"].lower():
                    self._correct(card)
                    return True
                self._reveal(card, wrong=ans.strip())
                return False

    def review_card(self, card, left):
        """REVIEW card: up to MAX_TRIES tries. Returns clean/dirty/skip/reveal."""
        show_tip = False
        tries = 0
        while True:
            self.card_header(card, left=left, review=True)
            self._draw_blank(card, show_tip, retry=tries)
            ans = read_line(center_plain("입력 ▶ ", TARGET))
            cmd = self._command(ans, card)
            if cmd == "tip":
                show_tip = True
                continue
            if cmd == "skip":
                self._reveal(card)
                return "skip"
            # an answer
            if ans.strip().lower() == card["answer"].lower():
                self._correct(card)
                return "clean" if tries == 0 else "dirty"
            tries += 1
            if tries >= MAX_TRIES:
                self._reveal(card)
                return "reveal"
            # else loop: let them try again

    def _command(self, ans, card):
        s = ans.strip().lower()
        if s in ("q", "quit", "exit"):
            raise ToMenu()
        if s in ("?", "힌트", "hint"):
            return "tip"
        if ans.strip() == "":
            return "skip"
        return "answer"

    def _draw_blank(self, card, show_tip, retry=0):
        visible, colored = sentence_line(card, fill=None)
        writeln(pad_center(cwidth(visible)) + colored)
        writeln()
        if show_tip:
            writeln(center_plain(card["tip"], DIM))
        else:
            writeln(center_plain("? 입력하면 힌트가 보여요", DIM))
        if retry:
            writeln(center_plain(f"다시 해봐요  ({retry}/{MAX_TRIES})", DANGER))
        else:
            writeln()
        writeln()
        writeln(center_plain("Enter(빈칸) 모르겠어요 · ? 힌트 · q 메뉴", DIM))
        writeln()

    def _correct(self, card):
        self.score += 10
        visible, colored = sentence_line(card, fill=card["answer"], fill_color=TYPED)
        # simple confirmation frame
        clear()
        _, rows = term_size()
        for _ in range(max(1, rows // 2 - 4)):
            writeln()
        writeln(center_plain(card["korean"], HINT))
        writeln()
        writeln(pad_center(cwidth(visible)) + colored)
        writeln()
        writeln(center_plain("✓  잘했어요!", TYPED + BOLD))
        sys.stdout.flush()
        time.sleep(ADVANCE_PAUSE)

    def _reveal(self, card, wrong=None):
        visible, colored = sentence_line(card, fill=card["answer"], fill_color=TARGET)
        clear()
        _, rows = term_size()
        for _ in range(max(1, rows // 2 - 5)):
            writeln()
        writeln(center_plain(card["korean"], HINT))
        writeln()
        writeln(pad_center(cwidth(visible)) + colored)
        writeln()
        if wrong:
            writeln(center_plain(f"✗  {wrong}", DANGER))
        writeln(center_plain(f"정답: {card['answer']}", TARGET + BOLD))
        writeln()
        read_line(center_plain("Enter ▶ 계속", DIM))

    # ---- between-stage screens ---------------------------------------------

    def summary(self, cards, weak, units):
        total, clean = len(cards), len(cards) - len(weak)
        pct = round(clean / total * 100)
        clear()
        _, rows = term_size()
        for _ in range(max(1, rows // 2 - 5)):
            writeln()
        writeln(center_plain("1차 결과", BOLD + INK))
        writeln()
        writeln(center_plain(f"맞은 문제  {clean} / {total}   ({pct}%)", INK))
        writeln(center_plain(f"복습할 문제  {len(weak)}개", HINT))
        writeln()
        if len(units) > 1:  # multi-unit diagnostic: show weak topics
            writeln(center_plain("약한 단원", HINT))
            for u in units:
                n = sum(1 for c in weak if c["unit_id"] == u["id"])
                if n:
                    writeln(center_plain(f"{u['title_ko']}  ·  {n}개", DIM))
            writeln()
        if read_line(center_plain("Enter ▶ 복습 시작 · q 메뉴", DIM)).strip().lower() == "q":
            raise ToMenu()

    def mastered(self, cleared):
        done = sum(1 for v in cleared.values() if v)
        total = len(cleared)
        remaining = total - done
        clear()
        _, rows = term_size()
        for _ in range(max(1, rows // 2 - 5)):
            writeln()
        title = "참 잘했어요!" if remaining == 0 else "거의 다 했어요!"
        writeln(center_plain("Done", BOLD + GOLD))
        writeln()
        writeln(center_plain(title, (TYPED if remaining == 0 else HINT) + BOLD))
        writeln()
        writeln(center_plain(f"맞힌 문제  {done} / {total}", INK))
        if remaining:
            writeln(center_plain(f"남은 {remaining}개는 다음에 또 풀어요", DIM))
        writeln()
        read_line(center_plain("Enter ▶ 메뉴", DIM))

    # ---- persistence -------------------------------------------------------

    def save(self):
        if not self.cards:
            return
        for u in self.units:
            weak = [c["idx"] for c in self.cards
                    if c["unit_id"] == u["id"]
                    and not self.cleared[(c["unit_id"], c["idx"])]]
            progress.update_unit(self.progress, u["id"], weak)
        progress.save(self.progress)


def _strip(s):
    """Remove ANSI codes so cwidth() measures only visible glyphs."""
    out, i = [], 0
    while i < len(s):
        if s[i] == "\x1b":
            j = s.find("m", i)
            i = (j + 1) if j != -1 else i + 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


if __name__ == "__main__":
    try:
        Game().run()
    finally:
        sys.stdout.write(RESET)
