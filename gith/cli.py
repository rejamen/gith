import typer
import subprocess
from typing import List
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

# TODO: implement better way of printint results, for example ERRORs

# TODO: test this outside. It shows the error, but still shows the empty table of branches.
def validate_git_repo():
    """
    Validate if Git is installed.
    """
    result = subprocess.run(["git", "status"], capture_output=True, text=True)
    if not result.returncode == 0:
        typer.echo("Error: Ensure you are in a Git repository.", err=True)

def list_git_branches() -> list:
    """
    Returns a list of local Git branches.
    """
    current = []
    others = []
    result = subprocess.run(["git", "branch"], capture_output=True, text=True)
    for branch in result.stdout.split("\n"):
        if branch.strip():
            name = branch.strip()
            if name.startswith("*"):
                current.append(name.replace('*', '').strip())
            else:
                others.append(name)
    return current + sorted(others)

def create_branch(branch_name: str, from_branch: int = 1):
    """
    Create a new branch in the Git repository.
    """
    # TODO: improve this code to always do:
    # 1. checkout to the branch if from_branch is provided, else stay in current branch
    # 2. pull the latest changes
    # 3. create a new branch from the current branch
    # If `from_branch` is None, then asume from_branch to be the current branch.
    branches = list_git_branches()
    if branch_name in branches:
        console.print(f"Sorry my friend, branch [green]{branch_name}[/green] already exists.")
        raise typer.Abort()
    
    if from_branch != 1:
        # TODO: try-catch
        # checkout to specified branch, pull the latest changes, and create a new branch from it.
        # TODO: do we stash before checkout?
        checkout_to_branch(branches[from_branch - 1])
    current_branch = branches[0]
    subprocess.run(["git", "pull", "origin", f"{current_branch}"], capture_output=True, text=True)
    result = subprocess.run(["git", "branch", branch_name], capture_output=True, text=True)
    if result.returncode == 0:
        console.print(f"New branch [green]{branch_name}[/green] created.")

def checkout_to_branch(branch_name: str):
    """
    Checkout to the specified branch.
    """
    result = subprocess.run(["git", "checkout", branch_name], capture_output=True, text=True)
    if result.returncode == 0:
        console.print(f"Switched to branch [green]{branch_name}[/green].")
    else:
        console.print(f"Error: Unable to switch to branch [red]{branch_name}[/red].")
        # TODO: improve how we show this error
        console.print(f"{result.stderr}")

def _process_str_indexes(indexes: str) -> list:
    """
    Process the string of indexes and return a list of integers.
    """
    try:
        return [int(index) for index in indexes.split(",")]
    except Exception as e:
        console.print(f"[red]Error[/red] processing provided indexes: {e}")
        raise typer.Abort()

def delete_branches(delete: str):
    """
    Delete branches by their indexes.
    """
    branches = list_git_branches()
    indexes = _process_str_indexes(delete)
    for index, branch_name in enumerate(branches, start=1):
        try:
            if index in indexes:
                result = subprocess.run(["git", "branch", "-D", branch_name], capture_output=True, text=True)
                if result.returncode == 0:
                    console.print(f"Branch [green]{branch_name}[/green] [red]deleted.[/red]")
                else:
                    console.print(f"Error: Unable to delete branch [red]{branch_name}[/red].")
        except Exception:
            console.print(f"Error: Branch with index [green]{index}[/green] [red]not found.[/red]")

def keep_branches(keep: str):
    """
    Keep the branches specified by indexes. Delete the rest.
    """
    branches = list_git_branches()
    indexes = _process_str_indexes(keep)
    for index, branch_name in enumerate(branches, start=1):
        try:
            if index not in indexes:
                result = subprocess.run(["git", "branch", "-D", branch_name], capture_output=True, text=True)
                if result.returncode == 0:
                    console.print(f"Branch [green]{branch_name}[/green] [red]deleted.[/red]")
                else:
                    console.print(f"Error: Unable to delete branch [red]{branch_name}[/red].")
        except Exception:
            console.print(f"Error: Branch with index [green]{index}[/green] [red]not found.[/red]")

@app.command()
def branch(
    list: bool = typer.Option(False, "--list", "-l", help="List local branches. Default behaviour if you call 'gith branch' without any options."),
    create: bool = typer.Option(False, "--create", "-c", help="Create a new branch."),
    branch_name: List[str] = typer.Argument(None, help="Name of the branch. You can use spaces in the name."),
    name_separator: str = typer.Option("_", help="Separator to use when creating a branch name with spaces. e.g: gith branch -c my new branch --name-separator -"),
    checkout: bool = typer.Option(True, help="Automatically checkout the new branch after creating it."),
    delete: str = typer.Option(False, "--delete", "-d", help="Delete branches by their indexes."),
    keep: str = typer.Option(False, "--keep", "-k", help="Keep the branches specified by indexes. CAUTION: this will delete the other branches."),
    from_branch: int = typer.Option(None, "--from", "-f", help="Index of the branch to create a new branch from. e.g: 'gith branch -c new_branch from 2' will create a new branch from 2."),
):
    """
    A helper command to list local Git branches.
    """
    validate_git_repo()
    if delete != 'False' and keep != 'False':  # TODO: find the best way to check this.
        console.print("[red]Error:[/red] You can not use 'delete' and 'keep' options together. Please use only one.")
        console.print(
            (
                "[yellow]Reminder:[/yellow] Use gith branch --delete 1,4,5 to delete branches of those indexes.\n"
                "Use gith branch --keep 6,9 to keep branches of those indexes and DELETE the rest."
            )
        )
        raise typer.Abort()

    # TODO: find the best way to detect the action
    if delete != 'False':
        delete_branches(delete)
    elif keep != 'False':
        keep_branches(keep)
    elif list or not list and not create and not branch_name:
        # then return default, which is list
        # TODO: check best way to do this
        branches = list_git_branches()
        table = Table()
        # Add columns to the table
        table.add_column("Index", justify="right", style="cyan", no_wrap=True)
        table.add_column("Branch Name")

        # Add rows
        for index, branch in enumerate(branches, start=1):
            if index == 1:
                # Highlight the current branch with green color
                table.add_row(str(index), branch, style="green")
            else:
                table.add_row(str(index), branch)
        # Print the table to the console
        console.print(table)
    elif create:
        if not branch_name:
            typer.echo(
                "Error: Please provide a branch name. e.g: gith branch -c my_new_branch.",
                err=True
            )
        else:
            branch_name = f"{name_separator}".join(branch_name)
            create_branch(branch_name, from_branch)
            if checkout:
                checkout_to_branch(branch_name)


@app.command()
def checkout(index: int):
    """
    A helper command to checkout to a branch by its index.
    """
    checkout_to_branch(list_git_branches()[index - 1])


if __name__ == "__main__":
    # TODO: explore, test, implement autocompletion
    app()
