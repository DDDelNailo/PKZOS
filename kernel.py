import pygame
import itertools
from logger import Logger
from window import Window
from constants import FLAGS
from app_base import BaseApp
from typing import TypedDict, Type, List, Tuple, Optional, Any, Dict

from apps.logger import LoggerApp
from apps.counter import CounterApp


class AppRegistry(TypedDict):
    app: Type[BaseApp]
    running: List[int]
    message_queue: List[Dict[str, Any]]


class Kernel:
    def __init__(self, screen_size: Tuple[int, int]) -> None:
        self.windows: list[Window] = []
        self.id_counter = itertools.count(1)
        self.screen_width, self.screen_height = screen_size

        Logger.log("main", "Kernel", "Initializing app registry")
        self.app_registry: dict[str, AppRegistry] = {
            "counter": {"app": CounterApp, "running": [], "message_queue": []},
            "logger": {"app": LoggerApp, "running": [], "message_queue": []},
        }

    def launch_app(
        self,
        namespace: str,
        title: Optional[str] = None,
        size: tuple[int, int] = (300, 200),
        pos: tuple[int, int] = (100, 100),
        flags: FLAGS = FLAGS(0),
    ) -> Optional[int]:
        Logger.log("main", "Kernel", f"Launching app '{namespace}'")

        app_registry = self.app_registry.get(namespace)
        if app_registry is None:
            Logger.error("main", "Kernel", f"App '{namespace}' not found")
            return
        app_class = app_registry.get("app")
        app = app_class(self, namespace)

        rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        wid = next(self.id_counter)
        window = Window(
            wid,
            app,
            rect,
            title=title or getattr(app, "title", f"app-{wid}"),
            embedded=bool(FLAGS.EMBEDDED & flags),
        )
        app.window = window

        try:
            app.on_launch()
        except Exception as e:
            Logger.error("main", "Kernel", f"App '{namespace}' launch error: {e}")
            return

        self.windows.append(window)
        self.bring_to_front(window.id)
        Logger.log("main", "Kernel", f"App '{namespace}' launched with id {window.id}")
        self.app_registry[namespace]["running"].append(window.id)
        return window.id

    def find_window_by_id(self, wid: Optional[int]) -> Optional[Window]:
        if wid is None:
            return None

        for w in self.windows:
            if w.id == wid:
                return w
        return None

    def bring_to_front(self, wid: int) -> None:
        Logger.log("main", "Kernel", f"Bringing window with id {wid} to front")
        w = self.find_window_by_id(wid)
        if not w:
            Logger.error("main", "Kernel", f"Window with id {wid} not found")
            return

        self.windows = [x for x in self.windows if x.id != wid]
        self.windows.append(w)

        for win in self.windows:
            win.active = win.id == wid

    def close_window(self, wid: int) -> None:
        Logger.log("main", "Kernel", f"Closing window with id {wid}")
        w = self.find_window_by_id(wid)
        if not w:
            Logger.error("main", "Kernel", f"Window with id {wid} not found")
            return

        try:
            w.app.on_close()
        except Exception as e:
            Logger.error("main", "Kernel", f"App {wid} close error: {e}")
            return

        self.windows = [x for x in self.windows if x.id != wid]
        self.app_registry[w.app.namespace]["running"].remove(w.id)

        if self.windows:
            self.windows[-1].active = True

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for win in reversed(self.windows):
                if win.contains_point(event.pos):
                    if win != self.windows[-1]:
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
            registry = self.app_registry.get(win.app.namespace)
            if registry is not None:
                while len(registry["message_queue"]) > 0:
                    win.app.listen(registry["message_queue"].pop(0))
            win.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        for win in self.windows:
            win.draw(surface)

    def queue_messge(self, namespace: str, data: dict[str, Any]) -> None:
        if namespace not in self.app_registry:
            return

        self.app_registry[namespace]["message_queue"].append(data)
