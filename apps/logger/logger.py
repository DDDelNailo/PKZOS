import pygame
from typing import List
from app_base import BaseApp


from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kernel import Kernel


class LoggerApp(BaseApp):
    def __init__(self, kernel: "Kernel", namespace: str) -> None:
        super().__init__(kernel, namespace, title="Logger")
        self.lines: List[str] = []
        self.max_lines = 200
        self.font = pygame.font.Font("fonts/DMMono.ttf", 16)
        self.bg = (0, 0, 0)

    def listen(self, data: dict[str, Any]) -> None:
        if data.get("type") != "log":
            return

        channel = data.get("channel", "")
        message = data.get("message", "")
        if not message:
            return

        self.lines.append(f"[{channel}] {message}")
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines :]

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self.bg)
        font_height = self.font.get_height()
        y = surface.get_height() - font_height - 4

        for line in reversed(self.lines):
            surf = self.font.render(line, True, (220, 220, 220))
            surface.blit(surf, (4, y))

            y -= font_height + 4
            if y < 0:
                break
