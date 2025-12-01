from typing import TYPE_CHECKING, Any, Dict, Callable, Generator, Tuple, TypeAlias

if TYPE_CHECKING:
    from kernel import Kernel

CommandType: TypeAlias = Callable[["Kernel", list[Any]], Generator[str, None, None]]


@staticmethod
def cmd_help(kernel: "Kernel", args: list[Any]) -> Generator[str, None, None]:
    yield "Available: " + ", ".join(kernel.command_registry.keys())


@staticmethod
def cmd_echo(kernel: "Kernel", args: list[Any]) -> Generator[str, None, None]:
    yield " ".join(args)


@staticmethod
def cmd_exit(kernel: "Kernel", args: list[Any]) -> Generator[str, None, None]:
    kernel.close_window(kernel.windows[-1].id)
    yield ""


class InternalCmds:
    @classmethod
    def get_cmds(cls) -> Generator[Tuple[str, CommandType], None, None]:
        cmds: Dict[str, CommandType] = {
            "help": cmd_help,
            "echo": cmd_echo,
            "exit": cmd_exit,
        }
        for name, cmd in cmds.items():
            yield name, cmd
