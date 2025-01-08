from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class GithConsole:
    """A wrapper class for Rich console functionality to provide consistent styling and formatting.
    
    This class provides methods for printing formatted messages, panels, and tables
    using the Rich library's features for enhanced terminal output.
    """
    def __init__(self):
        """Initialize a new GithConsole instance with a Rich console object."""
        self.console = Console()

    def print_message(self, message: str) -> None:
        """Print a regular message to the console.
        
        Args:
            message (str): The message to print
        """
        self.console.print(message)

    def print_panel(
        self,
        message: str,
        title: str,
        border_style: str = "default",
        title_align: str = "left",
    ) -> None:
        """Print a message in a bordered panel with a title.
        
        Args:
            message (str): The message to display inside the panel
            title (str): The title of the panel
            border_style (str, optional): The color/style of the panel border. Defaults to "default"
            title_align (str, optional): Title alignment ("left", "center", "right"). Defaults to "left"
        """
        panel = Panel(
            message, title=title, border_style=border_style, title_align=title_align
        )
        self.console.print(panel)

    def print_table(self, columns: list[dict], rows: list[dict]):
        """Print data in a formatted table with customizable columns.
        
        Args:
            columns (list[dict]): List of column definitions with format:
                {
                    'name': str,       # Column header
                    'justify': str,    # Text alignment
                    'style': str,      # Color/style
                    'no_wrap': bool    # Text wrapping
                }
                e.g:  columns = [
                    {"name": "Column 1", "justify": "right"},
                    {"name": "Column 2", "justify": "left"},
                ]
        
            rows (list[dict]): List of row data matching column definitions:
                {
                    'data': list,      # Row cell values
                    'style': str       # Color/style
                }
                e.g:  rows = [
                    {"data": ["value1", "value2"], "style": "green"},
                    {"data": ["value3", "value4"], "style": "red"},
                ]
        """
        table = Table()

        # Add columns to the table
        for column in columns:
            table.add_column(
                column.get("name"),
                justify=column.get("justify", "right"),
                style=column.get("style", "default"),
                no_wrap=column.get("no_wrap", True),
            )

        # Add rows
        for row in rows:
            table.add_row(*row["data"], style=row.get("style", "default"))

        self.print_message(table)
