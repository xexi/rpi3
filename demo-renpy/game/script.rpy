# Math quiz demo — three multiple-choice questions in Korean.
# No image assets required: backgrounds are solid colors so the project
# runs on a fresh install with nothing but Ren'Py + Noto CJK font.
#
# Authoring pattern: one `menu:` per question. Each choice is a label
# (or inline block) that adjusts $ score and prints feedback.

define teacher = Character("선생님", color="#42a5f5")

# Solid-color "scenes" — Ren'Py treats hex strings as 1-color images.
image bg classroom = "#fce4b3"
image bg right     = "#a5d6a7"
image bg wrong     = "#ef9a9a"

default score = 0

label start:
    $ score = 0
    scene bg classroom
    teacher "안녕! 오늘은 짧은 수학 퀴즈를 풀어볼게요."
    teacher "총 3문제예요. 준비됐나요?"

    # ---------- Q1 ----------
    scene bg classroom
    teacher "사과가 3개 있어요. 2개를 더 받으면 모두 몇 개일까요?"
    menu:
        "4개":
            call wrong_feedback("정답은 5개예요.")
        "5개":
            call right_feedback
        "6개":
            call wrong_feedback("정답은 5개예요.")

    # ---------- Q2 ----------
    scene bg classroom
    teacher "강아지가 4마리, 고양이가 2마리 있어요. 동물은 모두 몇 마리?"
    menu:
        "5마리":
            call wrong_feedback("정답은 6마리예요.")
        "6마리":
            call right_feedback
        "8마리":
            call wrong_feedback("정답은 6마리예요.")

    # ---------- Q3 ----------
    scene bg classroom
    teacher "쿠키 10개를 친구 2명과 똑같이 나누면 한 명은 몇 개?"
    menu:
        "3개":
            call wrong_feedback("정답은 5개예요. 10 ÷ 2 = 5")
        "5개":
            call right_feedback
        "10개":
            call wrong_feedback("정답은 5개예요. 10 ÷ 2 = 5")

    # ---------- Result ----------
    scene bg classroom
    teacher "퀴즈가 끝났어요! [score]점 / 3점 받았어요."
    if score == 3:
        teacher "완벽해요! 별 셋!"
    elif score >= 2:
        teacher "잘했어요! 별 둘!"
    else:
        teacher "다시 도전해봐요! 별 하나."

    return


label right_feedback:
    scene bg right
    $ score += 1
    teacher "정답이에요! 잘했어요."
    return

label wrong_feedback(hint):
    scene bg wrong
    teacher "다시 생각해볼까요? [hint]"
    return
