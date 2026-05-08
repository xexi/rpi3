# Project metadata + Korean font wiring.
#
# We reference the font as a path relative to game/. setup-renpy.sh copies
# a system Korean font (Noto CJK on Linux, AppleGothic on macOS) into
# game/fonts/Korean.ttf at install time.
#
# Why relative + ttf only: Ren'Py 8.x is unreliable at loading absolute
# paths to system fonts and at picking the right face inside .ttc files.
# A single-face .ttf in the project directory is the boring path that
# always works.

define config.name = _("수학 퀴즈 데모")
define config.version = "0.1"
define gui.show_name = True

define gui.text_font = "fonts/Korean.ttf"
define gui.name_text_font = "fonts/Korean.ttf"
define gui.interface_text_font = "fonts/Korean.ttf"

# CRITICAL: gui.text_font only takes effect through screens.rpy, which this
# minimal project doesn't ship. The actual rendering reads style.default.font,
# so override it directly. All other styles inherit from default.
init python:
    style.default.font = "fonts/Korean.ttf"
    style.default.size = 36
    style.button_text.font = "fonts/Korean.ttf"
    style.say_dialogue.font = "fonts/Korean.ttf"
    style.say_label.font = "fonts/Korean.ttf"
    style.input.font = "fonts/Korean.ttf"

# Bigger text — easier on a kid + a small Pi monitor.
define gui.text_size = 36
define gui.name_text_size = 42
define gui.button_text_size = 32

define config.window_title = "수학 퀴즈 데모"

# Skip the "Are you sure you want to quit?" prompt. Ren'Py 8.5.2's default
# quit screen requires a screens.rpy we don't ship, and crashes without it.
define config.quit_action = Quit(confirm=False)
