import pygame
import itertools
from window import Window
from typing import Tuple, Optional

from app_base import BaseApp


class Kernel:
    def __init__(self, screen_size: Tuple[int, int]) -> None:
        self.windows: list[Window] = []
        self.id_counter = itertools.count(1)
        self.screen_width, self.screen_height = screen_size

    def launch_app(
        self,
        app_class: type[BaseApp],
        title: Optional[str] = None,
        size: tuple[int, int] = (300, 200),
        pos: tuple[int, int] = (100, 100),
    ):
        app = app_class(self)
        wid = next(self.id_counter)
        rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        window = Window(
            wid, app, rect, title=title or getattr(app, "title", f"app-{wid}")
        )
        app.window = window

        try:
            app.on_launch()
        except Exception as e:
            print(f"[kernel] app.on_launch error: {e}")

        self.windows.append(window)
        self.bring_to_front(window.id)
        return window.id

    def find_window_by_id(self, wid: int) -> Optional[Window]:
        for w in self.windows:
            if w.id == wid:
                return w
        return None

    def bring_to_front(self, wid: int) -> None:
        w = self.find_window_by_id(wid)
        if not w:
            return

        self.windows = [x for x in self.windows if x.id != wid]
        self.windows.append(w)

        for win in self.windows:
            win.active = win.id == wid

    def close_window(self, wid: int) -> None:
        w = self.find_window_by_id(wid)
        if not w:
            return

        try:
            w.app.on_close()
        except Exception as e:
            print(f"[kernel] app.on_close error: {e}")

        self.windows = [x for x in self.windows if x.id != wid]

        if self.windows:
            self.windows[-1].active = True

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for win in reversed(self.windows):
                if win.contains_point(event.pos):
                    self.bring_to_front(win.id)
                    win.handle_event(event)
                    return

            for win in self.windows:
                win.active = False

            return

        if self.windows:
            top = self.windows[-1]
            top.handle_event(event)

    def update(self, dt: float) -> None:
        for win in self.windows:
            win.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        for win in self.windows:
            win.draw(surface)
