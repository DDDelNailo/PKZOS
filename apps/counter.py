import pygame
from typing import Tuple
from app_base import BaseApp
from logger import Logger


from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kernel import Kernel


class CounterApp(BaseApp):
    def __init__(self, kernel: "Kernel", namespace: str) -> None:
        super().__init__(kernel, namespace, title="Counter App")
        self.counter = 0
        self.font = pygame.font.Font(None, 20)
        self.bg: Tuple[int, int, int] = (40, 40, 40)

    def listen(self, data: dict[str, Any]) -> None:
        if data.get("type") != "set_value":
            return

        value = data.get("value", "")
        if not value:
            return

        self.counter = value

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.counter += 1
            self.kernel.queue_message(
                "counter",
                {"mode": "broadcast", "type": "set_value", "value": self.counter},
            )
            Logger.info(f"Counter updated to {self.counter}", "counter")

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self.bg)

        text = f"Clicks: {self.counter}"

        surf = self.font.render(text, True, (220, 220, 220))
        surface.blit(surf, (8, 8))
