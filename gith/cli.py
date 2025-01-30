import typer
from rich.console import Console
from typing import List

from .helpers import gith
from .messages import GithMessage, GithMessageLevel
from pathlib import Path
import yaml

app = typer.Typer()
console = Console()


def get_config_path() -> Path:
    """
    Get the path to the configuration file.
    """
    return Path.home() / ".githconfig"


def load_config() -> dict:
    """
    Load the configuration file.
    """
    config_path = get_config_path()
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}

config = load_config()

def branch_name_autocomplete(ctx: typer.Context, incomplete: str) -> List[str]:
    """
    Autocomplete function for branch names.
    """
    branches = gith.git_branch(verbose=False)
    return [
        f"{i} -> {name}"
        for i, name in enumerate(branches, start=1)
        if name.startswith(incomplete)
    ]


def validate_commands(delete: str, keep: str):
    """
    Validate the delete and keep commands.
    """
    if delete != "False" and keep != "False":  # TODO: find the best way to check this.
        # show info before error, as error will automatically abort the program.
        GithMessage(
            (
                "Use gith branch --delete 1,4,5 to delete branches of those indexes.\n"
                "Use gith branch --keep 6,9 to keep branches of those indexes and DELETE the rest."
            ), GithMessageLevel.INFO

        )
        GithMessage(
            "You can not use 'delete' and 'keep' options together. Please use only one.",
            GithMessageLevel.ERROR
        )


@app.command()
def branch(
    list: bool = typer.Option(
        False,
        "--list", "-l",
        help="List local branches. Default behaviour if you call 'gith branch' without any option.",
    ),
    create: bool = typer.Option(False, "--create", "-c", help="Create a new branch."),
    branch_name: List[str] = typer.Argument(None, help="Name for the new branch. You can use spaces in the name."),
    name_separator: str = typer.Option("_", help="Separator to use when creating a branch name with spaces."),
    checkout: bool = typer.Option(True, help="Automatically checkout the new branch after creating it."),
    delete: str = typer.Option(
        False,
        "--delete", "-d",
        help="Delete branches by their indexes. Autocompletion available.",
        autocompletion=branch_name_autocomplete,
    ),
    keep: str = typer.Option(
        False,
        "--keep", "-k",
        help="Keep the branches specified by indexes and delete the other branches. Autocompletion available.",
        autocompletion=branch_name_autocomplete,
    ),
    from_branch: int = typer.Option(
        1,
        "--from", "-f",
        help="Specify a branch index from where to create a new branch. Autocompletion available.",
        autocompletion=branch_name_autocomplete,
    ),
):
    """
    A helper command to work with Git local branches.
    """
    gith.validate_git_repo()
    validate_commands(delete, keep)
    # TODO: find the best way to detect the action
    if delete != "False":
        gith.delete_branches(delete)
    elif keep != "False":
        gith.keep_branches(keep)
    elif list or not list and not create and not branch_name:
        gith.git_branch()
    elif create:
        # get name_separator from config file
        name_separator = config.get("name_separator", False) or name_separator
        name = f"{name_separator}".join(branch_name)
        gith.create_branch(name, from_branch, checkout, name_separator)
        if checkout:
            gith.checkout_to_branch(name)


@app.command()
def checkout(
    index: int = typer.Argument(
        ...,
        help="Index of the branch to checkout to. Autocompletion available.",
        autocompletion=branch_name_autocomplete,
    ),
    pull: bool = typer.Option(
        True,
        help="Pull the latest changes from the remote repository after switching branches.",
    ),
):
    """
    A helper command to checkout to a branch by its index.
    """
    branches = gith.git_branch(verbose=False)
    branch_to_checkout = branches[index - 1]
    gith.checkout_to_branch(branch_to_checkout)
    if pull:
        gith.git_pull(branch_to_checkout)


if __name__ == "__main__":
    app()
