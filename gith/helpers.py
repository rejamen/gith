import os
import subprocess

from .console import GithConsole
from .messages import GithMessage, GithMessageLevel

console = GithConsole()


class GithHelper:
    def validate_git_repo(self) -> None:
        """
        Validate if Git is installed.
        """
        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        if not result.returncode == 0:
            GithMessage(f"{result.stderr}", GithMessageLevel.ERROR)

    def git_branch(self, verbose: bool = True) -> list[str]:
        """
        Returns a list of local Git branches.

        First branch in the list is the current branch, the rest are sorted alphabetically.

        Args:
            verbose (bool, optional): Print the branches in a table. Defaults to True.
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
        branches = current + sorted(others)
        if verbose:
            self.print_branches(branches)
        return branches
    
    def print_branches(self, branches: list) -> None:
        """
        Print the branches in a formatted table.

        Args:
            branches (list[str]): List of branch names
        """
        columns = [
            {"name": "Index", "justify": "right"},
            {"name": "Branch Name", "justify": "left"},
        ]
        rows = [
            {
                "data": [str(index), branch],
                "style": f"{'green' if index == 1 else 'default'}"
            }
            for index, branch in enumerate(branches, start=1)
        ]
        console.print_table(columns, rows)

    def create_branch(
        self,
        branch_name: str,
        from_branch: int,
        checkout: bool = False,
        name_separator: str = "_"
    ) -> None:
        """
        Create a new branch in the Git repository.

        1. checkout to the branch if from_branch != 1, else stay in current branch
        2. pull the latest changes. It might happens that this branch does not exist on the remote, try catch the error,
        ignore it, and just show an info message. This is not an error that will block the branch creation.
        3. create a new branch from the current branch
        4. checkout to the new branch if checkout is True

        Args:
            branch_name (str): The name of the new branch.
            from_branch (int, optional): The index of the branch to create the new branch from. Defaults to 1.
            checkout (bool, optional): Checkout to the new branch after creating it. Defaults to False.
            name_separator (str, optional): The separator to use when creating a branch name with spaces. Defaults to "_".
        """
        branches = gith.git_branch(verbose=False)
        current_branch = branches[0]
        if from_branch != 1:
            self.checkout_to_branch(branches[from_branch - 1], verbose=False)
            current_branch = branches[from_branch - 1]

        try:
            self.git_pull(current_branch)
        except Exception:
            GithMessage(
                f"Error while pulling from [green]{current_branch}[/green]. This will not block the branch creation.",
                GithMessageLevel.INFO
            )
        result = subprocess.run(
            ["git", "branch", branch_name], capture_output=True, text=True
        )
        if result.returncode == 0:
            message = (
                f"New branch [green]{branch_name}[/green] created "
                f"from [green]{current_branch}[/green]."
            )
            GithMessage(message, GithMessageLevel.LOG)
        else:
            GithMessage(f"Error creating branch: {result.stderr}", GithMessageLevel.ERROR)

    def checkout_to_branch(self, branch_name: str, verbose: bool = True) -> None:
        """
        Checkout to the specified branch.

        Args:
            branch_name (str): The name of the branch to checkout to.
            verbose (bool, optional): Print a message if the branch is switched. Defaults to True.
        """
        result = subprocess.run(
            ["git", "checkout", branch_name], capture_output=True, text=True
        )
        if result.returncode == 0 and verbose:
            GithMessage(f"Switched to branch [green]{branch_name}[/green].", GithMessageLevel.LOG)
        elif result.returncode != 0:
            GithMessage(f"{result.stderr}", GithMessageLevel.ERROR)

    def delete_branches(self, delete: str) -> None:
        """
        Delete branches by their indexes.

        Args:
            delete (str): Comma-separated list of branch indexes
        """
        branches = gith.git_branch(verbose=False)
        indexes = self.get_indexes_from_str(delete)
        for index, branch_name in enumerate(branches, start=1):
            try:
                if index in indexes:
                    result = subprocess.run(
                        ["git", "branch", "-D", branch_name],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        GithMessage(f"Deleting [green]{branch_name}[/green]", GithMessageLevel.LOG)
                    else:
                        GithMessage(f"{result.stderr}", GithMessageLevel.ERROR, abort=False)
            except Exception as e:
                GithMessage(f"{e}", GithMessageLevel.ERROR, abort=False)
        GithMessage("Process [green]Done.[/green]", GithMessageLevel.LOG)
        # show the updated branches again
        gith.git_branch()
    
    def keep_branches(self, keep: str):
        """
        Keep the branches specified by indexes. Delete the rest.

        Args:
            keep (str): Comma-separated list of branch indexes to keep
        """
        branches = gith.git_branch(verbose=False)
        indexes = self.get_indexes_from_str(keep)
        for index, branch_name in enumerate(branches, start=1):
            try:
                if index not in indexes:
                    result = subprocess.run(
                        ["git", "branch", "-D", branch_name], capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        GithMessage(f"Deleting [green]{branch_name}[/green]", GithMessageLevel.LOG)
                    else:
                        console.print(
                            f"Error: Unable to delete branch [red]{branch_name}[/red]."
                        )
            except Exception as e:
                GithMessage(f"{e}", GithMessageLevel.ERROR, abort=False)
        GithMessage("Process [green]Done.[/green]", GithMessageLevel.LOG)
        # show the updated branches again
        gith.git_branch()
    
    def get_indexes_from_str(self, indexes: str) -> list[int]:
        """
        Process the string of indexes and return a list of integers.

        Args:
            indexes (str): Comma-separated list of indexes
        """
        try:
            return [int(index) for index in indexes.split(",")]
        except Exception as e:
            GithMessage(f"Error processing provided indexes: {e}", GithMessageLevel.ERROR)

    def git_pull(self, branch_name: str) -> None:
        """
        Pull the latest changes from the specified branch.

        Args:
            branch_name (str): The name of the branch to pull changes from.
        """
        result = subprocess.run(
            ["git", "pull", "origin", branch_name], capture_output=True, text=True
        )
        if result.returncode == 0:
            GithMessage(f"Pulling changes from [green]{branch_name}[/green]", GithMessageLevel.LOG)
        else:
            GithMessage(f"{result.stderr}", GithMessageLevel.ERROR)

    def create_repo(self, url: str, config: dict) -> None:
        """Create a new local repository for the given URL.

        Check first if the command is executed from a folder with the same name as the repository.
        If not, then create a folder with the repository name and move into it.

        Args:
            url (str): Repository URL. e.g: git@github.com:rejamen/my_cool_project.git
            config (dict): Configuration options for the repository.
        """
        repo_name = url.split("/")[-1].replace(".git", "")
        current_folder = os.path.basename(os.getcwd())
        if current_folder != repo_name:
            try:
                os.makedirs(repo_name, exist_ok=True)
                os.chdir(repo_name)
                GithMessage(f"Created folder [green]{repo_name}[/green].", GithMessageLevel.LOG)
            except Exception as e:
                GithMessage(f"Error creating folder: {e}", GithMessageLevel.ERROR)
        self.git_init()
        self.set_main_branch("main")
        alias = config.get("alias", None)
        self.add_remote_url(url, alias)
        set_local_config = config.get('set_local_config', False) in ('True', 'true')
        if set_local_config:
            self.set_local_config(config)

    def git_init(self) -> None:
        """
        Initialize a new Git repository.
        """
        result = subprocess.run(["git", "init"], capture_output=True, text=True)
        if result.returncode == 0:
            GithMessage("Git repository initialized.", GithMessageLevel.LOG)
        else:
            GithMessage(f"Error initializing Git repository: {result.stderr}", GithMessageLevel.ERROR)
    
    def set_main_branch(self, branch_name: str) -> None:
        """
        Set the main branch for the Git repository.

        Args:
            branch_name (str): The name of the main branch.
        """
        result = subprocess.run(
            ["git", "branch", "-M", branch_name], capture_output=True, text=True
        )
        if result.returncode == 0:
            GithMessage(f"Main branch set to [green]{branch_name}[/green]", GithMessageLevel.LOG)
        else:
            GithMessage(f"Error setting main branch: {result.stderr}", GithMessageLevel.ERROR)
    
    def add_remote_url(self, url: str, alias: str=None) -> None:
        """
        Set the remote URL for the Git repository.

        Args:
            url (str): The remote URL to set.
            alias (str, optional): The alias for the remote. Defaults to None.
        """
        if alias:
            url = url.replace('github.com', alias)
        result = subprocess.run(
            ["git", "remote", "add", "origin", url], capture_output=True, text=True
        )
        if result.returncode == 0:
            GithMessage(f"Remote URL set to [green]{url}[/green]", GithMessageLevel.LOG)
        else:
            GithMessage(f"Error setting remote URL: {result.stderr}", GithMessageLevel.ERROR)

    def set_local_config(self, config: dict) -> None:
        """
        Set the local config for the Git repository.

        At the moment, only user.name and user.email are supported.

        Args:
            config (dict): Configuration options for the user data.
        """
        user_name = config.get("user_name", None)
        user_email = config.get("user_email", None)
        if not user_name or not user_email:
            GithMessage(
                "User name and email are required to set local user data. Check your gith.conf file.",
                GithMessageLevel.ERROR
            )
        result = subprocess.run(
            ["git", "config", "--local", "user.name", user_name],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            GithMessage(
                f"Local user.name set to [yellow]{user_name}[/yellow]",
                GithMessageLevel.LOG
            )
        else:
            GithMessage(
                f"Error setting local user name: {result.stderr}",
                GithMessageLevel.ERROR
            )
        
        result = subprocess.run(
            ["git", "config", "--local", "user.email", user_email],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            GithMessage(
                f"Local user.email set to [yellow]{user_email}[/yellow]",
                GithMessageLevel.LOG
            )
        else:
            GithMessage(
                f"Error setting local user email: {result.stderr}",
                GithMessageLevel.ERROR
            )

gith = GithHelper()
