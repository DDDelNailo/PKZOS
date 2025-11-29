import pygame

from pygame.event import Event
from app_base import BaseApp


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kernel import Kernel


class TerminalApp(BaseApp):
    def __init__(self, kernel: "Kernel", namespace: str) -> None:
        super().__init__(kernel, namespace, title="Terminal")
        self.lines: list[str] = []
        self.current: str = ""

        self.max_lines: int = 200
        self.font = pygame.font.Font("fonts/DMMono.ttf", 18)
        self.bg = (0, 0, 0)

        self.cursor_time: int = 0
        self.cursor_state: bool = True

    def send(self) -> None:
        self.lines.append(self.current)
        self.current = ""
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines :]

    def handle_event(self, event: Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.unicode and len(event.unicode) == 1 and event.unicode.isprintable():
            self.current += event.unicode
            return

        match event.key:
            case pygame.K_BACKSPACE:
                self.current = self.current[:-1]
            case pygame.K_RETURN | pygame.K_KP_ENTER:
                self.send()
            case _:
                return

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self.bg)
        font_height = self.font.get_height()
        y = surface.get_height() - font_height - 4

        self.cursor_time += pygame.time.get_ticks() % 50
        if self.cursor_time > 500:
            self.cursor_state = not self.cursor_state
            self.cursor_time = 0
        display_current = self.current + ("|" if self.cursor_state else "")

        for line in reversed(self.lines + [display_current]):
            surf = self.font.render(line, True, (220, 220, 220))
            surface.blit(surf, (4, y))

            y -= font_height + 4
            if y < 0:
                break

