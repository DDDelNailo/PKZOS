import pygame
from typing import Tuple
from app_base import BaseApp


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kernel import Kernel


class SampleApp(BaseApp):
    def __init__(self, kernel: "Kernel") -> None:
        super().__init__(kernel, title="Sample App")
        self.counter = 0
        self.font = pygame.font.Font(None, 20)
        self.bg: Tuple[int, int, int] = (40, 40, 40)

    def on_launch(self):
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.counter += 1

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self.bg)

        text = f"Clicks: {self.counter}"

        surf = self.font.render(text, True, (220, 220, 220))
        surface.blit(surf, (8, 8))
