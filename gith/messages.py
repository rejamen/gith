import typer
from enum import Enum

from .console import GithConsole


class GithMessageLevel(Enum):
    """Enumeration for message levels with associated colors."""
    INFO = ("info", "yellow")
    ERROR = ("error", "red")
    LOG = ("log", "default")

    def __init__(self, level: str, color: str):
        """
        Initialize a GithMessageLevel instance.

        Args:
            level (str): The message level (e.g., 'info', 'error', 'log').
            color (str): The color associated with the message level.
        """
        self.level = level
        self.color = color


class GithMessage:
    """Class for displaying messages with different levels using GithConsole."""

    def __init__(self, message: str, level: GithMessageLevel = GithMessageLevel.ERROR, abort=True):
        """
        Initialize a GithMessage instance.

        Args:
            message (str): The message to display.
            level (GithMessageLevel, optional): The level of the message. Defaults to GithMessageLevel.ERROR.
            abort (bool, optional): Whether to abort the program if the message level is ERROR. Defaults to True.
        """
        self.console = GithConsole()
        self.message = message
        self.level = level
        self._print_message(abort)

    def _print_message(self, abort: bool):
        """
        Print the message in a panel with the appropriate level and color.
        
        Args:
            abort (bool): Whether to abort the program or not.
        """
        if self.level in (GithMessageLevel.ERROR, GithMessageLevel.INFO):
            self.console.print_panel(
                self.message, self.level.level.title().upper(), self.level.color
            )
            if self.level == GithMessageLevel.ERROR and abort:
                raise typer.Abort()
        elif self.level == GithMessageLevel.LOG:
            self.console.print_message(self.message)
