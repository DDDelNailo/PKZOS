from enum import IntFlag, auto

# Main
SCREEN_SIZE = (1280, 720)
FPS = 60
SCREEN_CAPTION = "PKZOS"

# Window
TITLEBAR_HEIGHT = 28
BORDER = 2
FONT_SIZE = 18


class FLAGS(IntFlag):
    EMBEDDED = auto()
