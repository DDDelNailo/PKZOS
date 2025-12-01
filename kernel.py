import pygame
import itertools
from logger import Logger
from window import Window
from constants import FLAGS
from app_base import BaseApp
from typing import (
    TypedDict,
    Type,
    List,
    Tuple,
    Optional,
    Any,
    Dict,
    Callable,
    Generator,
)

from apps.logger import LoggerApp
from apps.counter import CounterApp
from apps.terminal import TerminalApp


class AppRegistry(TypedDict):
    app: Type[BaseApp]
    running: List[int]
    message_queue: List[Dict[str, Any]]


class Kernel:
    def __init__(self, screen_size: Tuple[int, int]) -> None:
        self.windows: list[Window] = []
        self.id_counter = itertools.count(1)
        self.screen_width, self.screen_height = screen_size

        Logger.info("Initializing app registry", "kernel")
        self.app_registry: dict[str, AppRegistry] = {
            "counter": {"app": CounterApp, "running": [], "message_queue": []},
            "logger": {"app": LoggerApp, "running": [], "message_queue": []},
            "terminal": {"app": TerminalApp, "running": [], "message_queue": []},
        }

        Logger.info("Initializing command registry", "kernel")
        self.command_registry: Dict[
            str, Callable[["Kernel", list[Any]], Generator[str, None, None]]
        ] = {}

        self.register_command("help", self.cmd_help)
        self.register_command("echo", self.cmd_echo)

        Logger.info("Loading custom app commands", "kernel")
        for registry in self.app_registry.values():
            cmd_count = registry["app"].register_commands()
            if cmd_count == 0:
                continue

            Logger.info(
                f"Loaded {cmd_count} commands from app {registry['app'].__name__}",
                "kernel",
            )

            for name, callback in registry["app"].commands.items():
                self.register_command(name, callback)

    @staticmethod
    def cmd_help(kernel: "Kernel", args: list[Any]) -> Generator[str, None, None]:
        yield "Available: " + ", ".join(kernel.command_registry.keys())

    @staticmethod
    def cmd_echo(kernel: "Kernel", args: list[Any]) -> Generator[str, None, None]:
        yield " ".join(args)

    def launch_app(
        self,
        namespace: str,
        title: Optional[str] = None,
        size: tuple[int, int] = (300, 200),
        pos: tuple[int, int] = (100, 100),
        flags: FLAGS = FLAGS(0),
    ) -> Optional[int]:
        Logger.debug(f"Launching app '{namespace}'", "kernel")

        app_registry = self.app_registry.get(namespace)
        if app_registry is None:
            Logger.error(f"App '{namespace}' not found", "kernel")
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
            Logger.error(f"App '{namespace}' launch error: {e}", "kernel")
            return

        self.windows.append(window)
        self.bring_to_front(window.id)
        Logger.debug(f"App '{namespace}' launched with id {window.id}", "kernel")
        self.app_registry[namespace]["running"].append(window.id)
        return window.id

    def find_window_by_id(self, wid: Optional[int]) -> Optional[Window]:
        if wid is None:
            Logger.warn("find_window_by_id called with None", "kernel")
            return None

        for w in self.windows:
            if w.id == wid:
                return w

        Logger.warn(f"Window with id {wid} not found", "kernel")
        return None

    def bring_to_front(self, wid: int) -> None:
        Logger.debug(f"Bringing window {wid} to front", "kernel")
        w = self.find_window_by_id(wid)
        if not w:
            Logger.error(f"Cannot bring to front: no window {wid}", "kernel")
            return

        self.windows = [x for x in self.windows if x.id != wid]
        self.windows.append(w)

        for win in self.windows:
            win.active = win.id == wid

    def close_window(self, wid: int) -> None:
        Logger.debug(f"Closing window {wid}", "kernel")
        w = self.find_window_by_id(wid)
        if not w:
            Logger.error(f"Cannot close: window {wid} not found", "kernel")
            return

        try:
            w.app.on_close()
        except Exception as e:
            Logger.error(f"App {wid} close error: {e}", "kernel")
            return

        self.windows = [x for x in self.windows if x.id != wid]
        self.app_registry[w.app.namespace]["running"].remove(w.id)

        if self.windows:
            self.windows[-1].active = True
            Logger.debug(f"Window {self.windows[-1].id} is now active", "kernel")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for win in reversed(self.windows):
                if win.contains_point(event.pos):
                    if win != self.windows[-1]:
                        Logger.debug(
                            f"Window {win.id} clicked, bringing to front", "kernel"
                        )
                        self.bring_to_front(win.id)
                    win.handle_event(event)
                    return

            Logger.debug("Click on empty space, clearing active windows", "kernel")
            for win in self.windows:
                win.active = False
            return

        if self.windows:
            top = self.windows[-1]
            top.handle_event(event)

    def update(self, dt: float) -> None:
        broadcast_queue: Dict[str, List[Dict[str, Any]]] = {}

        for win in self.windows:
            namespace = win.app.namespace
            registry = self.app_registry.get(namespace)

            if registry and registry["message_queue"]:
                msg_count = len(registry["message_queue"])

                while registry["message_queue"]:
                    message = registry["message_queue"].pop(0)

                    mode = message.get("mode")

                    if namespace != "logger":
                        Logger.debug(
                            ("Broadcasting" if mode == "broadcast" else "Dispatching")
                            + f" {msg_count} messages to {namespace}",
                            "kernel",
                        )

                    if mode == "broadcast":
                        broadcast_queue.setdefault(namespace, []).append(message)
                    else:
                        try:
                            win.app.listen(message)
                        except Exception as e:
                            Logger.error(
                                f"App '{namespace}' listen() error: {e}", "kernel"
                            )

            try:
                win.update(dt)
            except Exception as e:
                Logger.error(f"App '{namespace}' update() error: {e}", "kernel")

        if broadcast_queue:
            for source_ns, messages in broadcast_queue.items():
                for msg in messages:
                    for win in self.windows:
                        if win.app.namespace != source_ns:
                            continue

                        try:
                            win.app.listen(msg)
                        except Exception as e:
                            Logger.error(
                                f"Broadcast to '{win.app.namespace}' failed: {e}",
                                "kernel",
                            )

    def draw(self, surface: pygame.Surface) -> None:
        for win in self.windows:
            win.draw(surface)

    def queue_message(self, namespace: str, data: dict[str, Any]) -> None:
        if namespace not in self.app_registry:
            return

        self.app_registry[namespace]["message_queue"].append(data)

    def register_command(
        self,
        name: str,
        handler: Callable[["Kernel", list[Any]], Generator[str, None, None]],
    ) -> None:
        if name in self.command_registry:
            Logger.error(
                f"Tried to register a command that already exists '{name}'", "kernel"
            )
            return

        self.command_registry[name] = handler

    def execute_command(self, raw: str) -> Generator[str, None, None]:
        if ";" in raw:
            for snippet in raw.strip().split(";"):
                yield from self.execute_command(snippet)
            return

        parts = raw.strip().split()
        if not parts:
            return

        name, *args = parts
        handler = self.command_registry.get(name)

        if handler is None:
            yield f"Command not found: {name}"
            return

        try:
            yield from handler(self, args)
        except Exception as e:
            yield f"Error executing {name}: {e}"
