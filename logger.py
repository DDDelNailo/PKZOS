from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Dict, Any
import time

if TYPE_CHECKING:
    from kernel import Kernel


class Logger:
    kernel: Optional["Kernel"] = None
    buffer: List[Dict[str, Any]] = []

    @staticmethod
    def format_timestamp() -> str:
        return time.strftime("%H:%M:%S")

    @classmethod
    def log(
        cls,
        message: str,
        channel: str,
        level: str = "INFO",
    ) -> None:
        text = f"{cls.format_timestamp()} [{level}] {message}"

        cls.buffer.append({"type": "log", "message": text, "channel": channel})

        cls.flush(channel)

    @classmethod
    def flush(cls, channel: str) -> None:
        if cls.kernel is None:
            return

        while cls.buffer:
            entry = cls.buffer.pop(0)
            try:
                cls.kernel.queue_message("logger", entry)
            except Exception as e:
                print(f"[LOGGER] Failed to send to kernel ({channel}): {e}")
                cls.buffer.insert(0, entry)
                break

    @classmethod
    def info(cls, msg: str, channel: str) -> None:
        cls.log(msg, channel, "INFO")

    @classmethod
    def warn(cls, msg: str, channel: str) -> None:
        cls.log(msg, channel, "WARN")

    @classmethod
    def error(cls, msg: str, channel: str) -> None:
        cls.log(msg, channel, "ERROR")

    @classmethod
    def debug(cls, msg: str, channel: str) -> None:
        cls.log(msg, channel, "DEBUG")
