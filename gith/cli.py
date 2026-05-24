import configparser
import os
import sys
from pathlib import Path
from typing import Iterable, List, Optional

import typer
from rich.console import Console

from .helpers import gith
from .messages import GithMessage, GithMessageLevel

app = typer.Typer()
console = Console()


def read_config():
    config = configparser.ConfigParser()
    config_path = os.path.join(Path.home() / "gith.conf")
    if not os.path.exists(config_path):
        return {}
    try:
        config.read(config_path)
    except configparser.Error as exc:
        GithMessage(
            f"Could not parse config file [yellow]{config_path}[/yellow]: {exc}",
            GithMessageLevel.ERROR,
        )
    return {section: dict(config.items(section)) for section in config.sections()}


config = {}

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
        name_separator = config.get("branch", {}).get("name_separator", False) or name_separator
        name = f"{name_separator}".join(branch_name)
        gith.create_branch(name, from_branch, checkout, name_separator)
        if checkout:
            gith.checkout_to_branch(name)


@app.command()
def checkout(
    index: Optional[int] = typer.Argument(
        None,
        help="Index of the branch to checkout to. Autocompletion available.",
        autocompletion=branch_name_autocomplete,
    ),
    pull: bool = typer.Option(
        True,
        help="Pull the latest changes from the remote repository after switching branches.",
    ),
    directory: Optional[str] = typer.Option(
        None,
        "--dir",
        help="Directory containing multiple git repositories to checkout to the same branch.",
    ),
    branch: Optional[str] = typer.Option(
        None,
        "--branch",
        "-b",
        help="Branch name to checkout, used with --dir.",
    ),
):
    """
    A helper command to checkout to a branch by its index.
    """
    if directory:
        if not branch:
            GithMessage("--branch is required when using --dir.", GithMessageLevel.ERROR)
        gith.checkout_dir(directory, branch)
    else:
        if index is None:
            GithMessage(
                "Provide a branch index, or use --dir with --branch.",
                GithMessageLevel.ERROR,
            )
        branches = gith.git_branch(verbose=False)
        branch_to_checkout = branches[index - 1]
        gith.checkout_to_branch(branch_to_checkout)
        if pull:
            gith.git_pull(branch_to_checkout)


@app.command()
def repo(
    url: str = typer.Argument(None, help='URL of the repository to create. e.g: git@github.com:john/my_cool_project.git.'),
):
    """
    A helper command to create new Git repositories.
    """
    try:
        gith.create_repo(url, config.get('repo', {}))
    except Exception as e:
        GithMessage(e, GithMessageLevel.ERROR)


def _known_commands() -> set:
    """Return the set of command names registered on the Typer app."""
    names = set()
    for cmd in app.registered_commands:
        name = cmd.name or (cmd.callback.__name__ if cmd.callback else None)
        if name:
            names.add(name)
    return names


_PASSTHROUGH_FLAGS = {
    "--help", "-h",
    "--version",
    "--install-completion",
    "--show-completion",
}


def _resolve_default_argv(
    argv: List[str],
    known_commands: Iterable[str],
    cfg: dict,
) -> List[str]:
    """Return argv, possibly prepended with the default command from config.

    Rules:
    - If a known command is already present as the first arg, leave argv alone.
    - If the first arg is a top-level help/version flag, leave argv alone.
    - Otherwise, if [default].command is set, prepend it; if the configured
      command name is unknown, surface a clean error and exit non-zero.
    - If no default is configured, leave argv alone (Typer will show its
      usual "Missing command" error).
    """
    known = set(known_commands)
    default_cmd = (cfg.get("default", {}) or {}).get("command", "").strip()

    if argv and argv[0] in known:
        return argv
    if argv and argv[0] in _PASSTHROUGH_FLAGS:
        return argv

    if not default_cmd:
        return argv

    if default_cmd not in known:
        GithMessage(
            (
                f"Unknown default command [yellow]{default_cmd}[/yellow] in "
                f"[yellow]~/gith.conf[/yellow] under section [yellow]\\[default][/yellow]. "
                f"Known commands: {', '.join(sorted(known))}."
            ),
            GithMessageLevel.ERROR,
        )

    return [default_cmd, *argv]


def main():
    global config
    try:
        config = read_config()
        sys.argv = [
            sys.argv[0],
            *_resolve_default_argv(sys.argv[1:], _known_commands(), config),
        ]
    except typer.Abort:
        raise SystemExit(1)
    app()


if __name__ == "__main__":
    main()
