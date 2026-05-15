# Each entry: (english, korean, chunk_start, chunk_length, sound_label)
# chunk_start / chunk_length point to the phonics sound to practice within
# the english word. Indices are 0-based.

WORDS = [
    # digraph "sh" — initial
    ("ship",  "배",         0, 2, "sh"),
    ("shop",  "가게",       0, 2, "sh"),
    ("shell", "조개",       0, 2, "sh"),
    # digraph "sh" — final
    ("fish",  "물고기",     2, 2, "sh"),
    ("wish",  "소원",       2, 2, "sh"),

    # digraph "ch" — initial
    ("chip",  "칩",         0, 2, "ch"),
    ("chick", "병아리",     0, 2, "ch"),
    ("chin",  "턱",         0, 2, "ch"),
    # digraph "ch" — final
    ("beach", "해변",       3, 2, "ch"),
    ("lunch", "점심",       3, 2, "ch"),

    # digraph "th"
    ("thin",  "얇은",       0, 2, "th"),
    ("thick", "두꺼운",     0, 2, "th"),

    # ending blend "sk"
    ("mask",  "마스크",     2, 2, "sk"),
    ("desk",  "책상",       2, 2, "sk"),
    ("ask",   "묻다",       1, 2, "sk"),
    # beginning blend "sk"
    ("skip",  "건너뛰다",   0, 2, "sk"),
    ("sky",   "하늘",       0, 2, "sk"),

    # blend "st"
    ("stop",  "멈추다",     0, 2, "st"),
    ("star",  "별",         0, 2, "st"),
    ("nest",  "둥지",       1, 2, "st"),
    ("fast",  "빠른",       1, 2, "st"),

    # double consonant "ll"
    ("bell",  "종",         2, 2, "ll"),
    ("ball",  "공",         2, 2, "ll"),
    ("doll",  "인형",       2, 2, "ll"),

    # double consonant "ss"
    ("grass", "잔디",       3, 2, "ss"),
    ("kiss",  "뽀뽀",       2, 2, "ss"),

    # vowel team "ee"
    ("bee",   "벌",         1, 2, "ee"),
    ("tree",  "나무",       2, 2, "ee"),
    ("seed",  "씨앗",       1, 2, "ee"),

    # vowel team "oo"
    ("moon",  "달",         1, 2, "oo"),
    ("book",  "책",         1, 2, "oo"),
    ("pool",  "수영장",     1, 2, "oo"),

    # vowel team "ai"
    ("rain",  "비",         1, 2, "ai"),
    ("tail",  "꼬리",       1, 2, "ai"),

    # vowel team "oa"
    ("boat",  "배",         1, 2, "oa"),
    ("road",  "길",         1, 2, "oa"),
]
