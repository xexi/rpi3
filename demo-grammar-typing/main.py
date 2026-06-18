import random
import sys

import pygame

import progress
from items import CURRICULUM, iter_units

WIDTH, HEIGHT = 980, 640
FPS = 60

# Mastery loop tuning (settled in HANDOFF open questions):
MAX_TRIES = 5          # wrong letters in a review round before the answer is revealed
ADVANCE_MS = 450       # pause after completing a card before the next one

BG = (245, 240, 230)
CARD = (255, 255, 255)
CARD_SHADOW = (220, 215, 200)
INK = (40, 50, 70)
DIM = (170, 165, 155)
HINT = (220, 110, 90)
TYPED = (90, 180, 140)
TARGET = (90, 130, 220)
DANGER = (230, 90, 90)
ACCENT = (90, 130, 220)
SECTION = (120, 95, 70)
SEL = (225, 235, 250)
TIP = (150, 120, 90)

BADGE_COLOR = {
    "untouched": (200, 195, 185),
    "started": (230, 160, 60),
    "mastered": (90, 180, 140),
}


def find_korean_font():
    candidates = [
        "NanumGothic", "NanumBarunGothic",
        "NotoSansCJKkr", "NotoSansCJK", "NotoSansKR",
        "AppleSDGothicNeo", "AppleGothic",
    ]
    for name in candidates:
        path = pygame.font.match_font(name)
        if path:
            return path
    return None


def build_cards(units):
    """Flatten a list of unit dicts into per-item card dicts (pass-1 order)."""
    cards = []
    for unit in units:
        for idx, (before, answer, after, korean, cue) in enumerate(unit["items"]):
            cards.append({
                "unit_id": unit["id"],
                "idx": idx,
                "before": before,
                "answer": answer,
                "after": after,
                "korean": korean,
                "cue": cue,
                "tip": unit["tip"],
                "unit_title_ko": unit["title_ko"],
            })
    return cards


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Grammar Tap")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        ko = find_korean_font()
        kf = (lambda s: pygame.font.Font(ko, s)) if ko else (lambda s: pygame.font.SysFont(None, s))
        self.ko_gloss = kf(40)     # Korean meaning above the sentence
        self.ko_tip = kf(26)       # one-line Korean grammar tip
        self.ko_small = kf(24)     # hints / menu Korean
        self.ko_menu = kf(28)      # menu rows (mixed EN+KO)
        self.ko_head = kf(30)      # section headers / summary lines

        self.sentence_font = pygame.font.SysFont("arial", 48, bold=True)
        self.cue_font = pygame.font.SysFont("arial", 28)
        self.ui_font = pygame.font.SysFont("arial", 22, bold=True)
        self.title_font = pygame.font.SysFont("arial", 48, bold=True)

        self.progress = progress.load()
        self.menu_rows = self._build_menu_rows()
        self.menu_cursor = 0
        self.menu_scroll = 0
        self.show_tip = False   # tip is shown only while Tab is held
        self.state = "menu"

    # ---- menu --------------------------------------------------------------

    def _build_menu_rows(self):
        rows = [{"kind": "diagnostic"}]
        for section in CURRICULUM:
            rows.append({"kind": "section", "section": section})
            for unit in section["units"]:
                rows.append({"kind": "unit", "unit": unit})
        return rows

    def select_menu_row(self):
        row = self.menu_rows[self.menu_cursor]
        if row["kind"] == "diagnostic":
            units = [u for _, u in iter_units()]
        elif row["kind"] == "section":
            units = list(row["section"]["units"])
        else:
            units = [row["unit"]]
        self.start_pass1(units)

    # ---- run lifecycle -----------------------------------------------------

    def start_pass1(self, units):
        self.run_units = [u["id"] for u in units]
        self.cards = build_cards(units)
        self.results = {(c["unit_id"], c["idx"]): {"cleared": False} for c in self.cards}
        self.queue = self.cards
        self.card_idx = 0
        self.score = 0
        self.streak = 0
        self.show_tip = False
        self.reset_flash()
        self.load_card()
        self.state = "play"

    def finish_pass1(self):
        self.weak_after_pass1 = [c for c in self.cards if not self.results[self._key(c)]["cleared"]]
        self.pass1_total = len(self.cards)
        self.pass1_clean = self.pass1_total - len(self.weak_after_pass1)
        if not self.weak_after_pass1:
            self.go_mastered()
        else:
            self.state = "summary"

    def start_review(self):
        self.review_queue = list(self.weak_after_pass1)
        self.show_tip = False
        self.start_round()
        self.state = "review"

    def start_round(self):
        self.round_list = list(self.review_queue)
        random.shuffle(self.round_list)   # reshuffle the weak set each round
        self.round_idx = 0
        self.load_card()

    def end_round(self):
        if not self.review_queue:
            self.go_mastered()
        else:
            self.start_round()

    def go_mastered(self):
        self.save_progress()
        self.state = "mastered"

    def esc_to_menu(self):
        if self.state in ("play", "review", "summary"):
            self.save_progress()
        self.state = "menu"

    def save_progress(self):
        for uid in self.run_units:
            weak = [c["idx"] for c in self.cards
                    if c["unit_id"] == uid and not self.results[self._key(c)]["cleared"]]
            progress.update_unit(self.progress, uid, weak)
        progress.save(self.progress)

    # ---- card state --------------------------------------------------------

    @staticmethod
    def _key(card):
        return (card["unit_id"], card["idx"])

    @property
    def current(self):
        if self.state == "play":
            return self.queue[self.card_idx] if self.card_idx < len(self.queue) else None
        if self.state == "review":
            return self.round_list[self.round_idx] if self.round_idx < len(self.round_list) else None
        return None

    def load_card(self):
        self.typed = 0
        self.card_clean = True
        self.wrong_count = 0
        self.reveal = False
        self.advance_timer = 0

    def reset_flash(self):
        self.flash = 0
        self.flash_dur = 1
        self.flash_color = TYPED

    def _flash(self, color, dur):
        self.flash = dur
        self.flash_dur = dur
        self.flash_color = color

    def handle_key(self, ch):
        card = self.current
        if not card or self.advance_timer > 0 or not ch.isalpha():
            return
        target = card["answer"].lower()
        if self.typed < len(target) and target[self.typed] == ch.lower():
            self.typed += 1
            self._flash(TYPED, 220)
            if self.typed >= len(target):
                self.complete_card()
        else:
            self.card_clean = False
            self.streak = 0
            self.wrong_count += 1
            self._flash(DANGER, 220)
            if self.state == "review" and self.wrong_count >= MAX_TRIES:
                self.reveal = True

    def complete_card(self):
        card = self.current
        key = self._key(card)
        if self.card_clean:
            self.results[key]["cleared"] = True
            self.streak += 1
            self.score += 10
        if self.state == "review" and self.card_clean and card in self.review_queue:
            self.review_queue.remove(card)
        self._flash(TYPED, ADVANCE_MS)
        self.advance_timer = ADVANCE_MS

    def skip(self):
        card = self.current
        if not card or self.advance_timer > 0:
            return
        self.streak = 0
        if self.state == "review" and card in self.review_queue:
            self.review_queue.remove(card)   # dropped: stays weak in progress
        self.advance()

    def advance(self):
        if self.state == "play":
            self.card_idx += 1
            if self.card_idx >= len(self.queue):
                self.finish_pass1()
            else:
                self.load_card()
        elif self.state == "review":
            self.round_idx += 1
            if self.round_idx >= len(self.round_list):
                self.end_round()
            else:
                self.load_card()

    def update(self, dt):
        if self.flash > 0:
            self.flash = max(0, self.flash - dt)
        if self.advance_timer > 0:
            self.advance_timer -= dt
            if self.advance_timer <= 0:
                self.advance()

    # ---- drawing -----------------------------------------------------------

    def blit_center(self, surf, cx, y):
        self.screen.blit(surf, (cx - surf.get_width() // 2, y))

    def draw_menu(self):
        self.blit_center(self.title_font.render("Grammar Tap", True, INK), WIDTH // 2, 28)
        self.blit_center(self.ko_small.render("주제를 골라 연습해요 · 틀린 문제는 다시 풀어요",
                                              True, HINT), WIDTH // 2, 84)

        list_top, row_h = 124, 32
        visible = (HEIGHT - list_top - 50) // row_h
        if self.menu_cursor < self.menu_scroll:
            self.menu_scroll = self.menu_cursor
        elif self.menu_cursor >= self.menu_scroll + visible:
            self.menu_scroll = self.menu_cursor - visible + 1

        for i in range(self.menu_scroll, min(len(self.menu_rows), self.menu_scroll + visible)):
            row = self.menu_rows[i]
            y = list_top + (i - self.menu_scroll) * row_h
            if i == self.menu_cursor:
                pygame.draw.rect(self.screen, SEL, pygame.Rect(40, y - 2, WIDTH - 80, row_h),
                                 border_radius=8)
            if row["kind"] == "diagnostic":
                self.screen.blit(self.ko_menu.render("▶  전체 진단 (모든 단원)", True, ACCENT), (60, y))
            elif row["kind"] == "section":
                s = row["section"]
                txt = f"{s['section']}.  {s['title_en']}  ·  {s['title_ko']}"
                self.screen.blit(self.ko_head.render(txt, True, SECTION), (56, y))
            else:
                u = row["unit"]
                badge = progress.badge_for(self.progress, u["id"])
                cx, cy = 92, y + row_h // 2 - 2
                if badge == "untouched":
                    pygame.draw.circle(self.screen, BADGE_COLOR[badge], (cx, cy), 7, 2)
                else:
                    pygame.draw.circle(self.screen, BADGE_COLOR[badge], (cx, cy), 7)
                txt = f"{u['title_en']}  ·  {u['title_ko']}"
                self.screen.blit(self.ko_menu.render(txt, True, INK), (114, y))

        hint = self.ko_small.render("↑↓ 이동 · Enter 시작 · Esc 나가기", True, DIM)
        self.blit_center(hint, WIDTH // 2, HEIGHT - 36)

    def render_sentence_surfaces(self, card):
        """Return (surfaces, total_width) for before + slot + cue + after."""
        surfs = []
        if card["before"]:
            surfs.append(self.sentence_font.render(card["before"], True, INK))
        answer = card["answer"]
        for i in range(len(answer)):
            if i < self.typed:
                surfs.append(self.sentence_font.render(answer[i], True, TYPED))
            else:
                surfs.append(self.sentence_font.render("_", True, TARGET))
        if card["cue"]:
            surfs.append(self.cue_font.render(f" ({card['cue']})", True, DIM))
        if card["after"]:
            surfs.append(self.sentence_font.render(card["after"], True, INK))
        total = sum(s.get_width() for s in surfs)
        return surfs, total

    def draw_card(self):
        card = self.current
        if not card:
            return
        review = self.state == "review"

        # top bar
        mode = self.ko_small.render("복습" if review else "학습", True, ACCENT if review else INK)
        self.screen.blit(mode, (24, 18))
        self.screen.blit(self.ko_small.render(card["unit_title_ko"], True, DIM), (24, 46))
        if review:
            prog = self.ui_font.render(f"left  {len(self.review_queue)}", True, INK)
        else:
            prog = self.ui_font.render(f"{self.card_idx + 1} / {len(self.queue)}", True, INK)
        self.blit_center(prog, WIDTH // 2, 18)
        self.screen.blit(self.ui_font.render(f"Score  {self.score}", True, INK),
                         (WIDTH - 150, 18))

        # tip line — revealed only while Tab is held down
        if self.show_tip:
            self.blit_center(self.ko_tip.render(card["tip"], True, TIP), WIDTH // 2, 78)
        else:
            self.blit_center(self.ko_small.render("Tab 누르고 있으면 힌트가 보여요", True, DIM),
                             WIDTH // 2, 80)

        # card
        card_w, card_h = 860, 300
        rect = pygame.Rect(WIDTH // 2 - card_w // 2, 120, card_w, card_h)
        pygame.draw.rect(self.screen, CARD_SHADOW,
                         pygame.Rect(rect.x, rect.y + 5, card_w, card_h), border_radius=22)
        pygame.draw.rect(self.screen, CARD, rect, border_radius=22)

        self.blit_center(self.ko_gloss.render(card["korean"], True, HINT),
                         rect.centerx, rect.y + 44)

        if self.reveal:
            self.blit_center(self.ko_small.render(f"정답: {card['answer']}", True, ACCENT),
                             rect.centerx, rect.y + 110)

        surfs, total = self.render_sentence_surfaces(card)
        x = rect.centerx - total // 2
        line_mid = rect.bottom - 90
        for s in surfs:
            r = s.get_rect()
            r.left = x
            r.centery = line_mid
            self.screen.blit(s, r)
            x += s.get_width()

        hint = self.ko_small.render("Tab 힌트 · Enter 모르겠어요 · Esc 메뉴", True, DIM)
        self.blit_center(hint, WIDTH // 2, HEIGHT - 36)

    def draw_summary(self):
        # Korean title must use a Korean-capable font, not the arial title_font.
        self.blit_center(self.ko_gloss.render("1차 결과", True, INK), WIDTH // 2, 70)
        pct = round(self.pass1_clean / self.pass1_total * 100)
        lines = [
            f"맞은 문제  {self.pass1_clean} / {self.pass1_total}   ({pct}%)",
            f"복습할 문제  {len(self.weak_after_pass1)}개",
        ]
        y = 170
        for ln in lines:
            self.blit_center(self.ko_head.render(ln, True, INK), WIDTH // 2, y)
            y += 46

        if len(self.run_units) > 1:
            y += 14
            self.blit_center(self.ko_small.render("약한 단원", True, HINT), WIDTH // 2, y)
            y += 36
            for uid in self.run_units:
                n = sum(1 for c in self.weak_after_pass1 if c["unit_id"] == uid)
                if n:
                    title = next(c["unit_title_ko"] for c in self.cards if c["unit_id"] == uid)
                    self.blit_center(self.ko_small.render(f"{title}  ·  {n}개", True, INK),
                                     WIDTH // 2, y)
                    y += 32

        self.blit_center(self.ko_small.render("Enter ▶ 복습 시작 · Esc 메뉴", True, DIM),
                         WIDTH // 2, HEIGHT - 50)

    def draw_mastered(self):
        cleared = sum(1 for r in self.results.values() if r["cleared"])
        total = len(self.results)
        remaining = total - cleared
        title = "참 잘했어요!" if remaining == 0 else "거의 다 했어요!"
        self.blit_center(self.title_font.render("Done", True, INK), WIDTH // 2, HEIGHT // 2 - 130)
        self.blit_center(self.ko_gloss.render(title, True, TYPED if remaining == 0 else HINT),
                         WIDTH // 2, HEIGHT // 2 - 60)
        self.blit_center(self.ko_head.render(f"맞힌 문제  {cleared} / {total}", True, INK),
                         WIDTH // 2, HEIGHT // 2 + 10)
        if remaining:
            self.blit_center(self.ko_small.render(f"남은 {remaining}개는 다음에 또 풀어요", True, DIM),
                             WIDTH // 2, HEIGHT // 2 + 56)
        self.blit_center(self.ko_small.render("Enter ▶ 메뉴", True, DIM),
                         WIDTH // 2, HEIGHT - 50)

    def draw(self):
        self.screen.fill(BG)
        if self.state in ("play", "review") and self.flash > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill(self.flash_color)
            overlay.set_alpha(int(self.flash / self.flash_dur * 70))
            self.screen.blit(overlay, (0, 0))

        if self.state == "menu":
            self.draw_menu()
        elif self.state in ("play", "review"):
            self.draw_card()
        elif self.state == "summary":
            self.draw_summary()
        elif self.state == "mastered":
            self.draw_mastered()
        pygame.display.flip()

    # ---- input loop --------------------------------------------------------

    def on_key(self, event):
        if event.key == pygame.K_ESCAPE:
            if self.state == "menu":
                pygame.quit(); sys.exit()
            self.esc_to_menu()
            return

        if self.state == "menu":
            if event.key in (pygame.K_UP, pygame.K_k):
                self.menu_cursor = (self.menu_cursor - 1) % len(self.menu_rows)
            elif event.key in (pygame.K_DOWN, pygame.K_j):
                self.menu_cursor = (self.menu_cursor + 1) % len(self.menu_rows)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.select_menu_row()
        elif self.state in ("play", "review"):
            if event.key == pygame.K_TAB:
                self.show_tip = True          # hold to peek the grammar tip
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.skip()                   # Enter = "don't know", skip
            elif event.unicode:
                self.handle_key(event.unicode)
        elif self.state == "summary":
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.start_review()
        elif self.state == "mastered":
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.state = "menu"

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.on_key(event)
                if event.type == pygame.KEYUP and event.key == pygame.K_TAB:
                    self.show_tip = False
            if self.state in ("play", "review"):
                self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
