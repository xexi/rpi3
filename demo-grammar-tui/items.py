# Grammar Tap curriculum — Grammar in Use style.
#
# Tree: CURRICULUM -> sections -> units -> items.
#   item = (before, answer, after, korean, cue)
#     before / after : sentence text on each side of the blank ("" allowed)
#     answer         : single canonical token, compared case-insensitively
#     korean         : meaning gloss shown above the card
#     cue            : dimmed base form drawn by the blank ("" if none) —
#                      used for transformation units so the test is the
#                      grammar, not the vocabulary.
#   unit also has a Korean "tip" (one-line rule reminder, shown each card).
#
# Only the v1 units ship here. Deferred ("✎") units — negatives, do/does
# questions, question words — need spaces/apostrophes and a type-and-submit
# input buffer; see HANDOFF.md.

CURRICULUM = [
    {
        "section": 1, "title_en": "Be verbs", "title_ko": "be동사",
        "units": [
            {
                "id": 1, "title_en": "am / is / are", "title_ko": "be동사 현재",
                "tip": "I → am, He/She/It → is, You/We/They → are",
                "items": [
                    ("I ",    "am",  " happy.",   "나는 행복하다.",   ""),
                    ("He ",   "is",  " tall.",    "그는 키가 크다.",  ""),
                    ("She ",  "is",  " kind.",    "그녀는 친절하다.", ""),
                    ("It ",   "is",  " a dog.",   "그것은 개다.",     ""),
                    ("You ",  "are", " smart.",   "너는 똑똑하다.",   ""),
                    ("We ",   "are", " here.",    "우리는 여기 있다.", ""),
                    ("They ", "are", " friends.", "그들은 친구다.",   ""),
                ],
            },
            {
                "id": 2, "title_en": "was / were", "title_ko": "be동사 과거",
                "tip": "과거형: I/He/She/It → was, You/We/They → were",
                "items": [
                    ("I ",    "was",  " sick.",   "나는 아팠다.",     ""),
                    ("He ",   "was",  " late.",   "그는 늦었다.",     ""),
                    ("It ",   "was",  " cold.",   "날씨가 추웠다.",   ""),
                    ("You ",  "were", " right.",  "너는 옳았다.",     ""),
                    ("We ",   "were", " tired.",  "우리는 피곤했다.", ""),
                    ("They ", "were", " happy.",  "그들은 행복했다.", ""),
                ],
            },
        ],
    },
    {
        "section": 2, "title_en": "Present simple", "title_ko": "현재 시제",
        "units": [
            {
                "id": 4, "title_en": "verb + -s (he/she/it)",
                "title_ko": "3인칭 단수 동사",
                "tip": "He/She/It 다음 동사에는 -s/-es를 붙여요. go → goes",
                "items": [
                    ("He ",     "goes",  " to school.", "그는 학교에 간다.",   "go"),
                    ("She ",    "reads", " a book.",    "그녀는 책을 읽는다.", "read"),
                    ("It ",     "runs",  " fast.",      "그것은 빨리 달린다.", "run"),
                    ("He ",     "plays", " soccer.",    "그는 축구를 한다.",   "play"),
                    ("She ",    "likes", " milk.",      "그녀는 우유를 좋아한다.", "like"),
                    ("My dad ", "works", " hard.",      "우리 아빠는 열심히 일한다.", "work"),
                ],
            },
            {
                "id": 5, "title_en": "have / has", "title_ko": "have / has",
                "tip": "He/She/It → has, 나머지 → have",
                "items": [
                    ("I ",    "have", " a pen.",     "나는 펜이 있다.",   ""),
                    ("He ",   "has",  " a car.",     "그는 차가 있다.",   ""),
                    ("She ",  "has",  " long hair.", "그녀는 머리가 길다.", ""),
                    ("It ",   "has",  " four legs.", "그것은 다리가 네 개다.", ""),
                    ("We ",   "have", " a dog.",     "우리는 개가 있다.", ""),
                    ("They ", "have", " two cats.",  "그들은 고양이 두 마리가 있다.", ""),
                ],
            },
        ],
    },
    {
        "section": 3, "title_en": "Past simple", "title_ko": "과거 시제",
        "units": [
            {
                "id": 7, "title_en": "regular + -ed", "title_ko": "규칙 과거형",
                "tip": "규칙 과거형은 동사 끝에 -ed를 붙여요. play → played",
                "items": [
                    ("I ",    "played",  " soccer.", "나는 축구를 했다.",   "play"),
                    ("She ",  "walked",  " home.",   "그녀는 집에 걸어갔다.", "walk"),
                    ("We ",   "watched", " a movie.","우리는 영화를 봤다.", "watch"),
                    ("He ",   "wanted",  " water.",  "그는 물을 원했다.",   "want"),
                    ("They ", "looked",  " happy.",  "그들은 행복해 보였다.", "look"),
                    ("I ",    "helped",  " my mom.", "나는 엄마를 도왔다.", "help"),
                ],
            },
            {
                "id": 8, "title_en": "irregular past", "title_ko": "불규칙 과거형",
                "tip": "불규칙 과거형은 모양이 바뀌어요. go → went, eat → ate",
                "items": [
                    ("I ",    "went", " home.",     "나는 집에 갔다.",     "go"),
                    ("She ",  "ate",  " an apple.", "그녀는 사과를 먹었다.", "eat"),
                    ("He ",   "saw",  " a bird.",   "그는 새를 봤다.",     "see"),
                    ("We ",   "had",  " lunch.",    "우리는 점심을 먹었다.", "have"),
                    ("They ", "came", " late.",     "그들은 늦게 왔다.",   "come"),
                    ("I ",    "made", " a cake.",   "나는 케이크를 만들었다.", "make"),
                ],
            },
        ],
    },
    {
        "section": 4, "title_en": "Nouns & Articles", "title_ko": "명사와 관사",
        "units": [
            {
                "id": 9, "title_en": "a / an", "title_ko": "부정관사",
                "tip": "모음(a,e,i,o,u) 소리로 시작하면 an, 아니면 a",
                "items": [
                    ("I have ", "a",  " cat.",   "나는 고양이가 있다.", ""),
                    ("I see ",  "an", " apple.", "나는 사과를 본다.",   ""),
                    ("She has ","an", " egg.",   "그녀는 달걀이 있다.", ""),
                    ("He has ", "a",  " dog.",   "그는 개가 있다.",     ""),
                    ("It is ",  "an", " ant.",   "그것은 개미다.",     ""),
                    ("I want ", "a",  " book.",  "나는 책을 원한다.",   ""),
                    ("We see ", "an", " owl.",   "우리는 올빼미를 본다.", ""),
                ],
            },
            {
                "id": 10, "title_en": "a/an vs the", "title_ko": "정관사",
                "tip": "처음 말하거나 아무거나면 a/an, 정해진 그것이면 the",
                "items": [
                    ("I want ",   "a",   " banana.", "나는 바나나를 원한다.", ""),
                    ("Look at ",  "the", " moon.",   "달을 봐.",           ""),
                    ("Close ",    "the", " door.",   "문을 닫아.",         ""),
                    ("She has ",  "a",   " ball.",   "그녀는 공이 있다.",   ""),
                    ("Open ",     "the", " box.",    "상자를 열어.",       ""),
                    ("Pass me ",  "the", " salt.",   "소금 좀 건네줘.",    ""),
                ],
            },
            {
                "id": 11, "title_en": "plural -s / -es", "title_ko": "복수형",
                "tip": "여러 개면 -s, -s/-x/-ch로 끝나면 -es. box → boxes",
                "items": [
                    ("I see two ",  "cats",  ".",          "고양이 두 마리가 보인다.", "cat"),
                    ("Three ",      "dogs",  " run.",       "개 세 마리가 달린다.",   "dog"),
                    ("I have five ","books", ".",           "나는 책이 다섯 권 있다.", "book"),
                    ("Two ",        "boxes", " are here.",  "상자 두 개가 여기 있다.", "box"),
                    ("She has many ","toys", ".",           "그녀는 장난감이 많다.",  "toy"),
                    ("Four ",       "buses", " stop.",      "버스 네 대가 선다.",    "bus"),
                ],
            },
        ],
    },
    {
        "section": 5, "title_en": "Pronouns & Possessives", "title_ko": "대명사·소유격",
        "units": [
            {
                "id": 12, "title_en": "subject pronouns", "title_ko": "주격 대명사",
                "tip": "나=I, 너=you, 그=he, 그녀=she, 그것=it, 우리=we, 그들=they",
                "items": [
                    ("", "I",    " am a student.",   "나는 학생이다.",   ""),
                    ("", "You",  " are nice.",       "너는 착하다.",     ""),
                    ("", "He",   " is my dad.",      "그는 우리 아빠다.", ""),
                    ("", "She",  " is my mom.",      "그녀는 우리 엄마다.", ""),
                    ("", "It",   " is a cat.",       "그것은 고양이다.", ""),
                    ("", "We",   " are a team.",     "우리는 한 팀이다.", ""),
                    ("", "They", " are my friends.", "그들은 내 친구다.", ""),
                ],
            },
            {
                "id": 13, "title_en": "possessives (my/your/his/her)",
                "title_ko": "소유격",
                "tip": "나의=my, 너의=your, 그의=his, 그녀의=her, 우리의=our, 그들의=their",
                "items": [
                    ("This is ",       "my",    " bag.",  "이것은 내 가방이다.",   ""),
                    ("That is ",       "your",  " seat.", "저것은 네 자리다.",     ""),
                    ("This is ",       "his",   " car.",  "이것은 그의 차다.",     ""),
                    ("That is ",       "her",   " doll.", "저것은 그녀의 인형이다.", ""),
                    ("This is ",       "our",   " house.","이것은 우리 집이다.",   ""),
                    ("That is ",       "their", " dog.",  "저것은 그들의 개다.",   ""),
                    ("The cat licks ", "its",   " paw.",  "고양이가 자기 발을 핥는다.", ""),
                ],
            },
            {
                "id": 14, "title_en": "this / that / these / those",
                "title_ko": "지시사",
                "tip": "가까이=this/these, 멀리=that/those. 하나↔여럿",
                "items": [
                    ("", "This",  " is a pen.",    "이것은 펜이다.",   ""),
                    ("", "That",  " is a tree.",   "저것은 나무다.",   ""),
                    ("", "These", " are apples.",  "이것들은 사과다.", ""),
                    ("", "Those", " are birds.",   "저것들은 새다.",   ""),
                    ("", "This",  " is my book.",  "이것은 내 책이다.", ""),
                    ("", "Those", " are stars.",   "저것들은 별이다.", ""),
                ],
            },
        ],
    },
    {
        "section": 6, "title_en": "Prepositions", "title_ko": "전치사",
        "units": [
            {
                "id": 15, "title_en": "in / on / at (place)", "title_ko": "장소 전치사",
                "tip": "안=in, 위(접촉)=on, 한 지점=at. at home, on the desk",
                "items": [
                    ("The cat is ",  "in", " the box.",   "고양이가 상자 안에 있다.", ""),
                    ("The book is ", "on", " the desk.",  "책이 책상 위에 있다.",   ""),
                    ("She is ",      "at", " home.",      "그녀는 집에 있다.",     ""),
                    ("Birds are ",   "in", " the tree.",  "새들이 나무에 있다.",   ""),
                    ("The cup is ",  "on", " the table.", "컵이 식탁 위에 있다.",  ""),
                    ("We are ",      "at", " school.",    "우리는 학교에 있다.",   ""),
                ],
            },
            {
                "id": 16, "title_en": "in / on / at (time)", "title_ko": "시간 전치사",
                "tip": "시각=at, 요일/날짜=on, 월/계절=in. at 7, on Monday, in May",
                "items": [
                    ("I get up ",       "at", " seven.",   "나는 7시에 일어난다.",  ""),
                    ("We meet ",        "on", " Monday.",  "우리는 월요일에 만난다.", ""),
                    ("It snows ",       "in", " winter.",  "겨울에 눈이 온다.",    ""),
                    ("School starts ",  "in", " March.",   "3월에 학교가 시작한다.", ""),
                    ("I sleep ",        "at", " night.",   "나는 밤에 잔다.",      ""),
                    ("My birthday is ", "in", " May.",     "내 생일은 5월이다.",   ""),
                ],
            },
        ],
    },
    {
        "section": 7, "title_en": "There is / are", "title_ko": "there is/are",
        "units": [
            {
                "id": 17, "title_en": "there is / there are",
                "title_ko": "there is / are",
                "tip": "하나/셀 수 없으면 There is, 여럿이면 There are",
                "items": [
                    ("There ", "is",  " a cat.",      "고양이 한 마리가 있다.", ""),
                    ("There ", "are", " two dogs.",   "개 두 마리가 있다.",   ""),
                    ("There ", "is",  " milk.",       "우유가 있다.",        ""),
                    ("There ", "are", " many stars.", "별이 많이 있다.",     ""),
                    ("There ", "is",  " a book.",     "책 한 권이 있다.",    ""),
                    ("There ", "are", " three boys.", "남자아이 세 명이 있다.", ""),
                ],
            },
        ],
    },
]


def iter_units(curriculum=CURRICULUM):
    """Yield (section_dict, unit_dict) for every unit, in order."""
    for section in curriculum:
        for unit in section["units"]:
            yield section, unit


def unit_by_id(unit_id, curriculum=CURRICULUM):
    for _, unit in iter_units(curriculum):
        if unit["id"] == unit_id:
            return unit
    return None
