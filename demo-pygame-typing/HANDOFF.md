# HANDOFF — Phonics Tap

Pygame-CE phonics game for Korean kids learning English. Player sees an English
word with its Korean meaning, types only the highlighted phonics chunk
(digraph / blend / double letter / vowel team).

## Current state

Working. Run with `cd demo-pygame-typing && bash setup.sh`.

- `main.py` — single-file game, ~190 lines, `Game` class drives everything.
- `words.py` — 36 entries: `(english, korean, chunk_start, chunk_len, sound_label)`.
  All chunks are **contiguous 2-letter patterns**. Non-contiguous patterns
  (magic-e `a_e`, split digraphs) are deliberately out of scope for v1.
- `setup.sh` — venv + `pip install pygame-ce` + run.
- Korean fonts resolved via `find_korean_font()` — searches Nanum / Noto CJK
  on Linux, AppleSDGothic on macOS. Falls back to default if none found.

## What needs to change

### 1. Enlarge the Korean text

The Korean meaning above the word reads visually smaller than the English at
the same point size (Hangul glyphs are denser). Bump:

- `self.ko_font`  : 30 → **42**  (the meaning shown above the word)
- `self.ko_small` : 22 → **26**  (the bottom-left key hint line)

Both are set in `Game.__init__` in `main.py`. The card height (`card_h = 320`)
and the top margin of the Korean blit (`rect.y + 32`) may need a small bump
so the larger text still sits comfortably above the word; verify visually.

### 2. Auto-loop sound + word audio

When a word card appears, automatically speak the phonics chunk and then the
full word, **looping forever** until the player advances to the next word
(chunk completed, or `Tab` skip):

```
"ch"  →  pause 600ms  →  "chin"  →  pause 1500ms  →  repeat … indefinitely
```

Stop the loop the instant `self.typed >= length` (right when scoring fires).
Restart fresh when `idx` advances to the next word.

User decision: no max-repeat count. Loops until next word.

Implementation sketch in `Game`:

- `self.audio_chunk_snd`, `self.audio_word_snd` — `pygame.mixer.Sound` objects,
  loaded on word change (cache the chunk sound across words — there are only
  ~10 unique chunks, but ~36 unique words).
- `self.audio_phase`: `"chunk" | "gap1" | "word" | "gap2"`.
- `self.audio_timer_ms`: countdown to next phase transition.
- `update(dt)`: decrement timer; on zero, advance phase and either play the
  next clip or sit in a gap.
- Stop and clear on chunk completion, skip, or game-over.

Initialize mixer **before** `pygame.init()` to avoid Pi3 audio lag:

```python
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
```

### 3. Hybrid audio: human-recorded chunks + gTTS words

**Decision (set by user)**: do NOT use TTS for phonics chunks. Hybrid layout:

- **Chunks (~11 clips)** — record manually. Native English speaker, phone
  mic is fine. ~10-minute session covers every unique `sound_label` in
  `words.py`. The user has past bad experience with standard TTS on isolated
  phonemes like `"sh"` and `"ee"` — gTTS / Polly Standard say letter names
  ("see-aitch") instead of phonemes. Quality fix needs paid neural TTS with
  SSML `<phoneme alphabet="ipa">` (AWS Polly Neural, Azure Neural), which is
  more setup than recording. Human voice is also pedagogically better for
  kids learning phonics anyway.
- **Full words (~36 MP3s)** — generate with gTTS. Standard TTS handles full
  English words correctly; recording 36 of them manually is tedious.

Do **not** run any TTS engine at runtime. Pi3 can't drive a quality engine
without latency. Pre-generate once, ship as files.

#### Generator tool — `tools/gen_audio.py`

gTTS only, for the **words** half:

- Reads `words.py`, generates one MP3 per unique English word.
- Output: `assets/audio/words/<word>.mp3`.
- Skips files that already exist (cheap re-runs).
- `pip install gTTS`.

Wire `setup.sh` to call it if word audio is missing:
```sh
if [ ! -d assets/audio/words ] || [ -z "$(ls -A assets/audio/words 2>/dev/null)" ]; then
  pip install gTTS
  python tools/gen_audio.py
fi
```

#### Chunk recording

User (or a native speaker) records ~11 WAVs and drops them in
`assets/audio/chunks/<chunk>.wav`. Filenames match the `sound_label` field
in `words.py`. Full chunk list to record:

```
sh   ch   th   sk   st   ll   ss   ee   oo   ai   oa
```

The game should load whichever chunk file format exists (`.wav` or `.mp3`)
so a TTS fallback (below) still works.

#### Fallback if recordings aren't ready yet

If `assets/audio/chunks/<chunk>.wav` is missing at runtime, **fall back to
gTTS with a phonetic-spelling map** so the game stays usable while
recordings are pending. Add to `gen_audio.py` as an opt-in mode
(`--chunks-fallback`):

```python
CHUNK_TTS_FALLBACK = {
    "sh": "shhh",  "ch": "chuh",  "th": "thuh",
    "sk": "skuh",  "st": "stuh",
    "ll": "luh",   "ss": "sss",
    "ee": "eee",   "oo": "oooh",  "ai": "ay",  "oa": "oh",
}
```

Quality is mediocre but unblocks demoing. Real recordings drop in place
later — game code shouldn't care about the source.

#### Accent (deferred)

Don't pick a TTS accent yet. It only affects the **words** half (chunks
will be the recorder's voice). Default to `en-US` for now and revisit
after listening to a generated batch. If the recorder is a Korean English
teacher with a US accent, match `en-US`; UK speaker, switch to `en-GB`.

`.gitignore` `assets/audio/` so generated files aren't committed.
Consider committing the human-recorded chunks separately if size /
licensing is acceptable — they're the slowest-to-regenerate asset.

## Files to touch

```
demo-pygame-typing/
├── main.py                 EDIT — fonts, audio loop in Game
├── words.py                no schema change
├── setup.sh                EDIT — call gen_audio.py if word audio missing
├── requirements.txt        NEW — pygame-ce, gTTS
├── tools/
│   └── gen_audio.py        NEW — gTTS generator (words + chunks fallback)
└── assets/
    └── audio/              NEW — .gitignored except possibly chunks/
        ├── chunks/         ← human recordings (sh.wav, ch.wav, …)
        └── words/          ← gTTS-generated (ship.mp3, chin.mp3, …)
```

Also add `assets/audio/` to the project `.gitignore` (or just
`assets/audio/words/` if chunks should be committed).

## Testing checklist

- Larger Korean text doesn't overflow the card on the test display
  (default 900×600). Re-center / re-pad if it does.
- First chunk audible **before** kid starts typing — don't gate audio on
  input.
- Audio loop stops cleanly on chunk completion (no trailing word playback
  after success flash).
- Skip (Tab) interrupts current playback.
- Reset (Enter on done screen) starts a fresh audio loop on the first word.
- Game runs with chunks/ missing — falls back to gTTS phonetic spelling.
- Game runs with chunks/ populated — uses WAVs, ignores fallback.
- On Pi3: no audio crackling. If there is, try mixer buffer 1024 instead
  of 512.
- mp3 plays via SDL2_mixer in pygame-ce. If it doesn't on the target system,
  switch `gen_audio.py` to write `.ogg` (gTTS only outputs MP3; you'd need
  to convert with `pydub` + ffmpeg, or switch to a different TTS that
  outputs OGG).

## Out of scope for this pass

- Non-contiguous phonics patterns (magic-e, split digraphs).
- Per-pattern lesson grouping (current shuffle mixes all patterns).
- Score persistence / per-child profiles.
- Visual reward animations on chunk completion.
- Paid neural TTS (Polly / Azure) with SSML phoneme tags — viable future
  upgrade if the user later wants TTS-only with no recording, but adds
  cloud-account setup and isn't justified for v2.
