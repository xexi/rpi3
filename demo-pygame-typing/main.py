import random
import sys

import pygame

from words import WORDS

WIDTH, HEIGHT = 900, 600
FPS = 60

BG = (245, 240, 230)
CARD = (255, 255, 255)
CARD_SHADOW = (220, 215, 200)
INK = (40, 50, 70)
DIM = (200, 195, 185)
HINT = (220, 110, 90)
TYPED = (90, 180, 140)
TARGET = (90, 130, 220)
DANGER = (230, 90, 90)
ACCENT = (90, 130, 220)

ADVANCE_MS = 450


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


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Phonics Tap")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        ko_path = find_korean_font()
        self.ko_font = pygame.font.Font(ko_path, 30) if ko_path else pygame.font.SysFont(None, 30)
        self.ko_small = pygame.font.Font(ko_path, 22) if ko_path else pygame.font.SysFont(None, 22)
        self.word_font = pygame.font.SysFont("arial", 110, bold=True)
        self.label_font = pygame.font.SysFont("arial", 36, bold=True)
        self.ui_font = pygame.font.SysFont("arial", 22, bold=True)
        self.big_font = pygame.font.SysFont("arial", 56, bold=True)

        self.reset()

    def reset(self):
        self.queue = list(WORDS)
        random.shuffle(self.queue)
        self.idx = 0
        self.typed = 0
        self.score = 0
        self.streak = 0
        self.best_streak = 0
        self.flash = 0
        self.flash_dur = 1
        self.flash_color = TYPED
        self.advance_timer = 0
        self.state = "play"

    @property
    def current(self):
        return self.queue[self.idx] if self.idx < len(self.queue) else None

    def handle_key(self, ch):
        if self.state != "play" or not self.current or self.advance_timer > 0:
            return
        if not ch.isalpha():
            return
        ch = ch.lower()
        eng, ko, start, length, label = self.current
        chunk = eng[start:start + length]

        if chunk[self.typed] == ch:
            self.typed += 1
            self._flash(TYPED, 250)
            if self.typed >= length:
                self.score += 5 * length + self.streak
                self.streak += 1
                self.best_streak = max(self.best_streak, self.streak)
                self._flash(TYPED, ADVANCE_MS)
                self.advance_timer = ADVANCE_MS
        else:
            self.streak = 0
            self._flash(DANGER, 220)

    def _flash(self, color, dur):
        self.flash = dur
        self.flash_dur = dur
        self.flash_color = color

    def update(self, dt):
        if self.flash > 0:
            self.flash = max(0, self.flash - dt)
        if self.advance_timer > 0:
            self.advance_timer -= dt
            if self.advance_timer <= 0:
                self.idx += 1
                self.typed = 0
                if self.idx >= len(self.queue):
                    self.state = "done"

    def draw_word_card(self):
        eng, ko, start, length, label = self.current

        sound = self.label_font.render(f"sound:  {label}", True, ACCENT)
        self.screen.blit(sound, (WIDTH // 2 - sound.get_width() // 2, 55))

        card_w, card_h = 720, 320
        card_x = WIDTH // 2 - card_w // 2
        card_y = 150
        pygame.draw.rect(self.screen, CARD_SHADOW,
                         pygame.Rect(card_x, card_y + 5, card_w, card_h), border_radius=22)
        rect = pygame.Rect(card_x, card_y, card_w, card_h)
        pygame.draw.rect(self.screen, CARD, rect, border_radius=22)

        ko_surf = self.ko_font.render(ko, True, HINT)
        self.screen.blit(ko_surf, (rect.centerx - ko_surf.get_width() // 2, rect.y + 32))

        chunk_complete = self.typed >= length
        surfs = []
        for i, c in enumerate(eng):
            in_chunk = start <= i < start + length
            if in_chunk:
                pos = i - start
                color = TYPED if pos < self.typed else TARGET
            else:
                color = INK if chunk_complete else DIM
            surfs.append(self.word_font.render(c, True, color))

        gap = 6
        total_w = sum(s.get_width() for s in surfs) + gap * (len(eng) - 1)
        x = rect.centerx - total_w // 2
        y = rect.bottom - 160
        for s in surfs:
            self.screen.blit(s, (x, y))
            x += s.get_width() + gap

    def draw_ui(self):
        score = self.ui_font.render(f"Score  {self.score}", True, INK)
        self.screen.blit(score, (24, 18))
        streak_color = ACCENT if self.streak >= 2 else INK
        streak = self.ui_font.render(f"Streak  {self.streak}", True, streak_color)
        self.screen.blit(streak, (WIDTH - streak.get_width() - 24, 18))
        progress = self.ui_font.render(f"{self.idx + 1} / {len(self.queue)}", True, INK)
        self.screen.blit(progress, (WIDTH // 2 - progress.get_width() // 2, HEIGHT - 38))
        hint = self.ko_small.render("Tab 건너뛰기  ·  Esc 나가기", True, DIM)
        self.screen.blit(hint, (24, HEIGHT - 38))

    def draw_done(self):
        title = self.big_font.render("Well done!", True, INK)
        sub = self.ko_font.render(
            f"점수 {self.score}  ·  최고 연속 {self.best_streak}  ·  Enter 다시하기",
            True, INK,
        )
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))
        self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 10))

    def draw(self):
        self.screen.fill(BG)

        if self.flash > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill(self.flash_color)
            overlay.set_alpha(int(self.flash / self.flash_dur * 70))
            self.screen.blit(overlay, (0, 0))

        if self.state == "play":
            self.draw_word_card()
            self.draw_ui()
        else:
            self.draw_done()

        pygame.display.flip()

    def skip(self):
        self.idx += 1
        self.typed = 0
        self.streak = 0
        if self.idx >= len(self.queue):
            self.state = "done"

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    if self.state == "done" and event.key == pygame.K_RETURN:
                        self.reset(); continue
                    if event.key == pygame.K_TAB and self.state == "play":
                        self.skip(); continue
                    if self.state == "play" and event.unicode:
                        self.handle_key(event.unicode)
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
