from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from kernel import Kernel


class Logger:
    enable_console: bool = False
    kernel: Optional["Kernel"] = None
    messages: list[str] = []

    @classmethod
    def set_output(cls, enable: bool) -> None:
        cls.enable_console = enable

    @classmethod
    def log(cls, file: str, source: str, message: str) -> None:
        if not cls.enable_console:
            return

        if source:
            message = f"[{source}] {message}"

        cls.messages.append(message)

        if cls.kernel is not None:
            while len(cls.messages) > 0:
                message = cls.messages.pop(0)
                cls.kernel.queue_messge("logger", {"type": "log", "message": message})

    @classmethod
    def warn(cls, file: str, source: str, message: str) -> None:
        if source:
            source = "WARN " + source
        else:
            source = "WARN"
        cls.log(file, source, message)

    @classmethod
    def error(cls, file: str, source: str, message: str) -> None:
        if source:
            source = "ERROR " + source
        else:
            source = "ERROR"
        cls.log(file, source, message)
