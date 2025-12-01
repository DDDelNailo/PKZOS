import pygame

from typing import Optional, TYPE_CHECKING, Any, Dict, Callable, Generator

if TYPE_CHECKING:
    from kernel import Kernel
    from window import Window


class BaseApp:
    commands: Dict[str, Callable[["Kernel", list[Any]], Generator[str, None, None]]] = (
        {}
    )

    def __init__(self, kernel: "Kernel", namespace: str, title: str = "App"):
        self.kernel = kernel
        self.namespace: str = namespace
        self.title = title
        self.window: Optional["Window"] = None

    @classmethod
    def register_commands(cls) -> int:
        """
        Called at kernel initialization to register custom app commands.
        """
        return 0

    def on_launch(self) -> None:
        """
        Called after the app is launched and the Window wrapper is attached.
        """
        pass

    def on_close(self) -> None:
        """
        Called when the app/window is closed.
        """
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Receive pygame events forwarded by the kernel/window.
        """
        pass

    def update(self, dt: float) -> None:
        """
        Update logic. dt = seconds since last frame.
        """
        pass

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the app's content into the given surface clipped to content_rect.
        surface: the main screen surface (blit only inside content_rect).
        content_rect: pygame.Rect indicating the drawable area for the app.
        """
        pass

    def listen(self, data: dict[str, Any]) -> None:
        pass
