# HANDOFF — Grammar Tap (design)

A pygame-CE **typing** game for Korean kids learning basic English grammar,
organized as a *Grammar in Use*–style course. The student picks a topic
(unit) from a table of contents, types the missing word in each sentence,
then the game **self-assesses** and re-drills only the items they got wrong
until every answer is correct.

> **Status: v1 built.** `main.py` + `items.py` + `progress.py` + `setup.sh`
> are working — run `bash setup.sh`. Decisions baked in: early-elementary
> vocab, `MAX_TRIES = 5`, mastery = every item typed clean, weak queue
> reshuffled each review round, one Korean tip per unit (**hold `Tab`** to
> peek). Ships the 15 `v1` units below (94 items); `✎` units remain deferred.
>
> **Controls (in a card):** type the answer · **hold `Tab`** to show the
> grammar tip · **`Enter`** = skip ("don't know") · `Esc` = back to menu.

## Why grammar, not phonics

Phonics Tap is blocked on audio (TTS reads isolated phonemes as letter
names; the Pi3 can't run a quality neural engine live). Grammar is **purely
textual** — no audio, no recordings, no TTS, no `assets/`. This pivot
sidesteps the exact blocker while reusing the typing engine that works.

## Audience & platform

- Korean kids, early English learners. Korean gloss shown with each sentence.
- Develop on macOS, **target Raspberry Pi 3** — pygame-CE only, light, no
  runtime codegen. Reuse `find_korean_font()` from the phonics demo.

## Core mechanic — fill-in-the-blank

One sentence per card, exactly one blank, one canonical answer. The student
types it letter by letter: each correct letter locks green, a wrong letter
flashes red and is ignored (retry — never stuck). Word complete → score,
flash, advance. Compare is **case-insensitive** (no Shift needed).

```
        그녀는 책을 읽는다
   ┌──────────────────────────────┐
   │   She  __ (read)  a book.     │   __ = blank (underscores) fills green
   │        ‾‾‾‾‾                  │   (read) = dimmed base-form cue
   └──────────────────────────────┘
        type the missing word
```

The dimmed `cue` (e.g. `(read)`) appears only for *transformation* units
(verb -s, plural, past tense) so the test is the **grammar**, not the
vocabulary. Other units have no cue.

---

## Curriculum — Table of Contents (*Grammar in Use* style)

The course is a tree: **Sections → numbered Units → items**. Units are the
unit of study and selection, exactly like Murphy's *Basic Grammar in Use*
(thematic sections, globally-numbered units, one grammar point each). The
menu (below) lets the student browse sections and pick a unit.

`v1` = answers are single tokens, ships in the first build.
`✎` = answers need spaces / apostrophes (negatives, questions) → deferred
until a type-and-submit buffer exists (see Out of scope).

### Section 1 · Be verbs — be동사
| Unit | Topic | 한국어 | |
|---|---|---|---|
| 1 | `am / is / are` | be동사 현재 | v1 |
| 2 | `was / were` | be동사 과거 | v1 |
| 3 | `is not / isn't` (negative) | be동사 부정 | ✎ |

### Section 2 · Present simple — 현재 시제
| Unit | Topic | 한국어 | |
|---|---|---|---|
| 4 | verb **+ -s** (he/she/it) | 3인칭 단수 동사 | v1 (cue) |
| 5 | `have / has` | have/has | v1 |
| 6 | `do / does` (questions) | 의문문 do/does | ✎ |

### Section 3 · Past simple — 과거 시제
| Unit | Topic | 한국어 | |
|---|---|---|---|
| 7 | regular **+ -ed** | 규칙 과거형 | v1 (cue) |
| 8 | irregular (go→went) | 불규칙 과거형 | v1 (cue) |

### Section 4 · Nouns & Articles — 명사와 관사
| Unit | Topic | 한국어 | |
|---|---|---|---|
| 9 | `a / an` | 부정관사 | v1 |
| 10 | `a/an` vs `the` | 정관사 | v1 |
| 11 | plural **-s / -es** | 복수형 | v1 (cue) |

### Section 5 · Pronouns & Possessives — 대명사·소유격
| Unit | Topic | 한국어 | |
|---|---|---|---|
| 12 | subject pronouns (I/he/she/they) | 주격 대명사 | v1 |
| 13 | possessives (my/your/his/her) | 소유격 | v1 |
| 14 | this / that / these / those | 지시사 | v1 |

### Section 6 · Prepositions — 전치사
| Unit | Topic | 한국어 | |
|---|---|---|---|
| 15 | `in / on / at` (place) | 장소 전치사 | v1 |
| 16 | `in / on / at` (time) | 시간 전치사 | v1 |

### Section 7 · There is/are & Questions — there/의문문
| Unit | Topic | 한국어 | |
|---|---|---|---|
| 17 | `there is / there are` | there is/are | v1 |
| 18 | question words (what/where/who) | 의문사 | ✎ |

v1 build ships the `v1`-marked units (≈13 units). Each unit holds ~8–12
items; the seed table below is representative, not the full set.

### Data model — `items.py`

```python
# Tree: sections -> units -> items.
# item = (before, answer, after, korean, cue)
#   before/after : sentence text around the blank (either may be "")
#   answer       : single canonical token, compared case-insensitively
#   korean       : meaning gloss shown above the card
#   cue          : dimmed base form by the blank, "" if none
CURRICULUM = [
  {
    "section": 1, "title_en": "Be verbs", "title_ko": "be동사",
    "units": [
      {
        "id": 1, "title_en": "am / is / are", "title_ko": "be동사 현재",
        "items": [
          ("I ",    "am",  " happy.",   "나는 행복하다.",  ""),
          ("He ",   "is",  " tall.",    "그는 키가 크다.", ""),
          ("They ", "are", " friends.", "그들은 친구다.",  ""),
        ],
      },
      # Unit 2: was/were ...
    ],
  },
  {
    "section": 4, "title_en": "Nouns & Articles", "title_ko": "명사와 관사",
    "units": [
      {
        "id": 9, "title_en": "a / an", "title_ko": "부정관사",
        "items": [
          ("I have ", "a",  " cat.",   "나는 고양이가 있다.", ""),
          ("I see ",  "an", " apple.", "나는 사과를 본다.",   ""),
        ],
      },
      {
        "id": 11, "title_en": "plural -s / -es", "title_ko": "복수형",
        "items": [
          ("I see two ", "cats",  ".",       "고양이 두 마리를 본다.", "cat"),
          ("Three ",     "boxes", " are here.","상자 세 개가 있다.",   "box"),
        ],
      },
    ],
  },
  # ...remaining sections
]
```

A flat helper (`all_units()`, `unit_by_id()`) walks the tree for the menu
and for cross-unit diagnostic runs.

---

## Menu — topic selection

A `menu` screen renders the TOC: section headers with their units listed
under each. Keyboard navigation (no mouse needed on the Pi):

- `↑ / ↓` move the cursor between units, `← / →` (or PgUp/PgDn) jump section.
- `Enter` opens the highlighted unit (starts a first pass on its items).
- Each unit row shows a **mastery badge** from saved progress:
  `○` untouched · `◐` started, weak items remain · `●` mastered (all clean).
- Top row offers two spanning modes:
  - **Section test** — run every v1 unit in a section as one diagnostic.
  - **Full diagnostic** — run all v1 units; the summary then reports weak
    *topics*, so "study the areas you're weak in" works at unit granularity.
- `Esc` quits.

Korean labels everywhere (`menu` reuses `ko_font`/`ko_small`).

---

## Self-assessment & mastery review loop

The heart of the new request: **solve once, then re-solve weak areas until
all correct.** Two-box (Leitner-lite) mastery.

### What counts as "weak"

Per item, the first time it's shown, record whether it was **clean**:

- **clean** = completed with **zero** wrong keystrokes and not skipped.
- **weak**  = any wrong letter typed before completing, **or** `Enter`-skipped.

(The char engine lets a kid retry a wrong letter, so "wrong keystroke" — not
"failed item" — is the precise weakness signal.)

### Flow

```
 select unit / test
        │
        ▼
 ┌─────────────────┐   every item shown once, in order
 │  PASS 1 (diag.) │   record clean / weak per item
 └─────────────────┘
        │
        ▼
 ┌─────────────────┐   accuracy, clean count, and — for multi-unit
 │  SELF-ASSESS    │   tests — a per-topic weak breakdown
 │  summary screen │   "N items to review."  Enter ▶ review
 └─────────────────┘
        │  (weak queue non-empty)
        ▼
 ┌─────────────────┐   re-serve ONLY weak items, shuffled.
 │  REVIEW ROUND   │   item leaves the queue when typed CLEAN this round;
 │  (repeat)       │   miss it again → it stays for the next round.
 └─────────────────┘
        │  queue empty
        ▼
 ┌─────────────────┐   "All correct! Unit mastered ●"
 │   MASTERED      │   save progress · Enter ▶ back to menu
 └─────────────────┘
```

- **Review serves only weak items** — the explicit ask. The student isn't
  re-typing things they already nailed.
- **Loop until empty.** Each round drains the queue of items typed clean
  that round; missed items roll to the next round. Converges to "all right."
- **Anti-frustration:** after `MAX_TRIES` wrong letters on one item in a
  review round, briefly reveal the answer (dim ghost text), let them copy
  it, and keep the item queued one more round. `Enter` (skip) drops an item
  from the queue, leaving it weak (counts against full mastery).
- **Multi-unit tests** group the weak queue's summary by unit so a student
  doing the Full diagnostic sees *which topics* to review, then the review
  rounds drill exactly those items.

### Progress persistence — `progress.json`

For a study tool, mastery must survive restarts (single local profile, no
accounts). Minimal JSON:

```json
{ "units": { "1": {"badge": "mastered", "weak_item_ids": []},
             "9": {"badge": "started",  "weak_item_ids": [3, 7]} } }
```

Item identity = stable index within its unit (the tuple's position).
Written on reaching MASTERED and on quitting mid-review (so a started unit
reopens straight into its remaining weak queue). Loaded at startup to paint
the menu badges. v1-recommended; if dropped, mastery is per-session only.

---

## Screen flow / states

```
menu  ──Enter──▶  pass1 ──done──▶  summary ──Enter──▶  review ──empty──▶  mastered ──Enter──▶ menu
  ▲                                                       │ (Enter/Esc)                          │
  └───────────────────────────────────────────────────────────────────────────────────────────┘
```

`Game.state ∈ {menu, play, summary, review, mastered}`. `play` and `review`
share the same card-drawing + char-validation code; they differ only in
which queue feeds them and what a result records (pass1 = mark clean/weak;
review = clear-on-clean / re-queue-on-miss).

## What carries over from Phonics Tap

`demo-pygame-typing/main.py`'s `Game` is the template:

- Per-char validation (`handle_key`), color scheme (green/blue/red flash),
  card + Korean gloss layout, `find_korean_font()`, score/streak/progress UI,
  advance timer. Keys are remapped: `Enter` skips, `Tab` holds the tip
  (phonics used `Tab` to skip).
- **Adopt the phonics font lesson:** Korean gloss ~42px, hint line ~26px.
- New vs phonics: `menu`/`summary`/`review`/`mastered` states, the
  curriculum tree, the weak-queue mastery loop, `progress.json`.
- Drop vs phonics: sentence font ~56–64px (whole sentence, not one word);
  keep sentences ≤ ~6 words, **single line, no wrapping** in v1.

## Files (no assets)

```
demo-grammar-typing/
├── main.py        NEW — Game (menu / play / summary / review / mastered)
├── items.py       NEW — CURRICULUM tree + helpers
├── progress.py    NEW — load/save progress.json (small)
├── setup.sh       NEW — venv + pip install pygame-ce + run (no gTTS)
└── HANDOFF.md     this design
```

No `assets/`, no `tools/`, only pygame-ce. `progress.json` is gitignored.

## Out of scope for v1

- **Audio of any kind** — the whole reason for the pivot.
- `✎` units (negatives, questions, do/does) — answers need spaces/
  apostrophes → require a type-and-submit input buffer instead of pure
  char-by-char. Plan that as v2's input mode.
- Multiple acceptable answers per blank; multi-line / wrapped sentences.
- Multiple child profiles (single local `progress.json` only).
- Spaced repetition across days, reward animations, sound.
- Word-order (SVO) and conjugation-only mechanics — possible sibling games.

## Decisions (resolved → built into v1)

1. **Target age / grade** — early elementary; ≤ 6-word sentences, common nouns.
2. **`MAX_TRIES` before the review answer-reveal** — 5 wrong letters.
3. **Mastery definition** — every item typed clean = unit mastered `●`.
4. **Review ordering** — weak queue reshuffled each round.
5. **Grammar tip** — one short Korean tip per unit, revealed only while
   `Tab` is held (a deliberate peek, not always-on); `Enter` is skip.
