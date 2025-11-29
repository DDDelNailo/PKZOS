from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from kernel import Kernel


class Logger:
    kernel: Optional["Kernel"] = None
    messages: list[str] = []

    @classmethod
    def log(cls, file: str, source: str, message: str) -> None:
        if source:
            message = f"[{source}] {message}"

        cls.messages.append(message)

        if cls.kernel is not None:
            while len(cls.messages) > 0:
                message = cls.messages.pop(0)
                data = {"type": "log", "message": message}
                cls.kernel.queue_messge("logger", data)

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
