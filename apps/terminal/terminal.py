import pygame

from pygame.event import Event
from app_base import BaseApp


from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from kernel import Kernel


class TerminalApp(BaseApp):
    def __init__(self, kernel: "Kernel", namespace: str) -> None:
        super().__init__(kernel, namespace, title="Terminal")
        self.lines: list[str] = []
        self.inp_history: list[str] = []
        self.inp_history_idx: Optional[int] = None
        self.inp_history_temp: str = ""
        self.current: str = ""
        self.current_prefix: str = "[root@pkzos /]$"

        self.max_lines: int = 200
        self.font = pygame.font.Font("fonts/DMMono.ttf", 18)
        self.bg = (0, 0, 0)

        self.cursor_time: int = 0
        self.cursor_state: bool = True

    def send(self) -> None:
        text = self.current.strip()
        self.inp_history.append(text)
        self.inp_history_idx = None
        self.lines.append(self.current_prefix + " " + text)
        self.current = ""
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines :]

        output = self.kernel.execute_command(text)
        if output:
            for line in output:
                self.lines.append(str(line))

    def handle_event(self, event: Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.unicode and len(event.unicode) == 1 and event.unicode.isprintable():
            self.current += event.unicode
            self.inp_history_idx = None
            return

        match event.key:
            case pygame.K_BACKSPACE:
                self.current = self.current[:-1]
            case pygame.K_RETURN | pygame.K_KP_ENTER:
                self.send()
            case pygame.K_UP:
                if self.inp_history_idx is None:
                    self.inp_history_idx = len(self.inp_history) - 1
                    if self.current:
                        self.inp_history_temp = self.current
                else:
                    self.inp_history_idx = max(self.inp_history_idx - 1, 0)

                self.current = self.inp_history[self.inp_history_idx]
            case pygame.K_DOWN:
                if self.inp_history_idx is not None:
                    self.inp_history_idx = min(
                        self.inp_history_idx + 1, len(self.inp_history)
                    )

                    if self.inp_history_idx == len(self.inp_history):
                        self.inp_history_idx = None
                        self.current = self.inp_history_temp
                    else:
                        self.current = self.inp_history[self.inp_history_idx]
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
        display_current = (
            self.current_prefix
            + " "
            + self.current
            + ("|" if self.cursor_state else "")
        )

        for line in reversed(self.lines + [display_current]):
            surf = self.font.render(line, True, (220, 220, 220))
            surface.blit(surf, (4, y))

            y -= font_height + 4
            if y < 0:
                break
