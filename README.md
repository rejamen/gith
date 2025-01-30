# Gith

Gith is a command-line interface (CLI) tool that simplifies Git operations. Built with [Typer](https://github.com/fastapi/typer)
, it streamlines your daily Git workflows and enhances productivity.

## When to use it?

Gith is particularly useful when you:

- Want a clear visual overview of all your local branches with their corresponding index numbers. These **indexes** will be very helpful when using **gith**
- Need to quickly switch between branches using simple index numbers instead of typing full branch names
- Work with branches that have long or complex names
- Want to create new branches with spaces in their names (automatically handled with separators)
- Need to perform bulk branch management operations (like keeping specific branches and removing others). Again, **indexes** will save your day.
- Creating a branch from another branch without the need of checkout to that branch. Use **index** to specify the origin branch instead.

Some examples:

- Instead of `git branch feature_user_auth_middleware`, use `gith branch -c feature user auth middleware`

- Instead of typing `git checkout user_authentication_middleware`, you can simply use `gith checkout 2` if that's the branch's index number.

- Instead of running `git branch -D` multiple times, use `gith branch -d 1,3,4` to delete branches by their indexes

- Instead of manually checking which branches to keep during cleanup, use `gith branch -k 1,2` to keep main branches and remove others

- Instead of typing `git checkout development && git pull && git checkout -b new_branch`, use `gith branch -c new branch --from 2` to create and switch to a new branch from development.

No need to memorize commands. Gith leverages Typer's built-in help system and shell autocompletion to provide:
- Instant access to command documentation via `--help`
- Tab completion for commands and options
- Interactive command suggestions 

## Installation

```bash
pip install gith
```

## Usage.

### Explore Gith commands and options.

The best way to get to know **gith** is by using the built-in help systems provided by Typer. Just type:

```bash
gith --help
```
and you get an output like this one, with an overview of the existing commands in **gith**
```shell
 Usage: gith [OPTIONS] COMMAND [ARGS]...

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                           │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                    │
│ --help                        Show this message and exit.                                                                         │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ branch     A helper command to work with Git local branches.                                                                      │
│ checkout   A helper command to checkout to a branch by its index.                                                                 │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Every command has its own set of options and expected arguments. So, again, let's get them using --help
```bash
gith branch --help
```
And you get all the available options for the `branch` command
```shell
 Usage: gith branch [OPTIONS] [BRANCH_NAME]...

 A helper command to work with Git local branches.

╭─ Arguments ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│   branch_name      [BRANCH_NAME]...  Name of the branch. You can use spaces in the name. [default: None]                          │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --list            -l                            List local branches. Default behaviour if you call 'gith branch' without any      │
│                                                 options.                                                                          |
│ --create          -c                            Create a new branch.                                                              │
│ --name-separator                       TEXT     Separator to use when creating a branch name with spaces. [default: _]            │
│ --checkout            --no-checkout             Automatically checkout the new branch after creating it. [default: checkout]      │
│ --delete          -d                   TEXT     Delete branches by their indexes. Autocompletion available. [default: False]      |
│ --keep            -k                   TEXT     Keep the branches specified by indexes and delete the other branches.             |
│                                                 [default: False]                                                                  │
│ --from            -f                   INTEGER  Specify a branch index from where to create a new branch.                         │
│                                                 Autocompletion available. [default: 1]                                            │
│ --help                                          Show this message and exit.                                                       │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```
As you can see, most of the options includes a more verbose part, like `gith branch --create` and a simpler version, like `gith branch -c`. Feel free to use the one you like it more. 

Just consider that at the time you are reading this, the implementation of **gith** might changed and the output could be different, but the way to get the information about the command will be the same, because of **Typer**

Let's explore every command with details.

## gith branch ...
### List local branches.
The fastest (and default) way to list branches with **gith** is:

```bash
gith branch
```
But you can also use `gith branch --list` or `gith branch -l`

In any case, the result will be a table where:
* Every branch will have an associated **index**.
* The first branch (**index = 1**) will always be the current branch and will be highlighted in green.
* The remaining branches will be listed in alphabetical order.

```bash
┏━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Index ┃ Branch Name   ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━┩
│     1 │ release_0.2.0 │
│     2 │ test_a        │
│     3 │ test_b        │
│     4 │ test_c        │
│     5 │ test_d        │
└───────┴───────────────┘
```

> The primary motivation for this command is to display all local branches with an assigned **index**. This index can then be used for various operations on the branch, eliminating the need to use the branch name. Additionally, listing the current branch at the top of the list, rather than the default Git method of marking it with an asterisk (*) and placing it alphabetically, makes it easier to locate when there are many local branches.

### Create a new branch.

Create a new local branch with the command:

```bash
gith branch --create new_branch_name
```
Or the simplified version: `gith branch -c my_new_branch`

As a result, a new branch will be created from your current branch.

Do you often use long names with special characters (like '-' or '_') and find it tedious to type them out? No worries, you can create branches using spaces like:
```
gith branch -c this is my branch name with spaces
```
The newly created branch will by default replace every space by an underscore ("_"), like: `this_is_my_branch_name_with_spaces`

Prefer a different separator? Use the command like this:
```
gith branch -c this is my branch name with spaces and other separator --name-separator -
```
This will replace the spaces with the specified separator: `this-is-my-branch-name-with-spaces-and-other-separator`

If you are not happy with the default separator and do not want to pass the `--name-separator` flag every time no worries, there is a possibility to add a `.githconfig` file and set this value. Continue reading until the section *Using a Configuration file*

In every of the previous cases, **gith** will **automatically checkout to the created branch** 😎

If you want to create your branch, wihtout doing checkout, then just call the command like:
```
gith branch -c this is my branch without checkout --no--checkout
```
And a new branch will be created from the current branch, named `this_is_my_branch_without_checkout` but you will stay in your current branch.

Last thing while creating branches. Does it often happen that you finish working on a branch and need to create another branch from, let's say, `staging-branch`, and you have to do:
```
git checkout staging-branch && git pull && git checkout -b staging-branch
```

Well, you can combine these three actions in a single command using **gith**. Assuming the index of **staging-branch** is `3`, no matter if you are already in that branch or not, you can:
```
gith branch -c new branch from staging without being in staging --from 3
```

This command will:
* Checkout to branch with index = 3 (staging-branch for the example)
* Excecute `git pull origin staging-branch` to update your local branch with the latests changes
* Create the new branch
* Checkout to that branch, unless you specifiy `--no-checkout`

> The motivation behind these options is to streamline the branch creation process. Typing branch names with spaces feels more intuitive. Additionally, creating a branch from another branch while ensuring the origin branch is automatically updated in a single command is a significant time saver.

### Delete branches by their indexes

Cleaning up local branches is maybe something you don't usually do, but when you do, oh boy, it's kind of a pain—at least for me. 😂 

If you want to delete several branches in one single command, just grab their indexes and use the following command:

```bash
gith branch --delete 3,5,2
```
Or the shorter version of the command `gith branch -d 3,5,2`.

Order does not matter, **gith** will order the given indexes and delete every branch. As you might guess, deleting current branch is not possible. So if you try `gith branch -d 1` you will get an error message. 

### Keep specific branches and delete the rest

Also, as part of the cleaning up process (why do I care about that? 🙄) maybe you want to delete all your branches but one. On this case, instead of using the previous command and being forced to type all the indexes, you better use this command:

```bash
gith branch --keep 1
```
This will delete all the other branches and keep only branch with index 1.

This command can be used in its shorter form as well, like `gith branch -k 1` and receive a comma-separated indexes, in case you want to keep more than one branch: `gith branch -k 1,3,6`

> The motivation behind the previous 2 commands was to improve the process of cleaning local branches. It saves me a lot of time when I can use one single command for that.

## gith checkout ...

As for the previous command, first, explore its options with:
```
gith checkout --help
```
```shell
Usage: gith checkout [OPTIONS] INDEX

 A helper command to checkout to a branch by its index.

╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    index      INTEGER  Index of the branch to checkout to. Autocompletion available. [default: None] [required]                      │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --pull    --no-pull      Pull the latest changes from the remote repository after switching branches. [default: pull]                  │
│ --help                   Show this message and exit.                                                                                   │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
### Checkout to a branch by its index

Changing branches is easier with **gith**. You can use branch index instead of name and you get **auto pulling from origin** by default 😎

```bash
gith checkout 2
```
If you want to checkout, but not pull, then call it like: `gith checkout 2 --no-pull`.

When you do checkout to a local branch that was not pushed yet to origin, you will get the following error, because that branch does not exist in remote, but it will not block the checkout process, so you are good to go.
```shell
╭─ ERROR ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ fatal: couldn't find remote ref test_branch                                                                                                 │
│                                                                                                                                        │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
> The motivation behind this command was to speed up the checkout process, ensuring automatic pull and branch handling by indexes.

## Enable autocompletion

One of the greatest things of **Typer** is enabling/using autocompletion 🚀

Use the following command to install automcompletion on your shell
```
gith --install-completion
```
You have to restart your console for this change to have effect. After you open a new console, now you can access all the **gith** commands and options using autocomplete.

For example, if you type `gith br` and hit TAB, it should autocomplete to `gith branch`. The same for `gith chec` TAB will autocomplete to `gith checkout`

Some options, like `delete`, `keep` and `from` has autocompletion enabled. You see it when typing `gith <command> --help` the options will say in the description **Autocompletion available.**

So, for example, if you want to delete some branches you need their **indexes**. You can of course do `gith branch` first, so you see the table with the branches and the indexes. But you can also do: `gith branch -d ` TAB
```
gith branch -d
1 -> test_a        3 -> test_c              5 -> test_e
2 -> test_b        4 -> test_d              6 -> test_f
$ gith branch -d
```
And you will get a list of local branches, with their indexes, so you can easily find the indexes without the need of typing an extra command.

## Using a configuration file
Adding a configuration file to set some default values while using **gith** is also possible. Right now, then only possible parameter to define is the `name_separator` used by the `gith branch -c` command, but in the future we might add other configurables there 😊

In order to change the default value of this command, follow these steps:

Create a file called `.githconfig` on your *Home* folder
```
nano ~/.githconfig
```
Add in this file the default separator you want to use while creating branches with spaces in the name. 
```yaml
name_separator: "-"
```
After that, you will be able to use `gith branch -c my branch name with spaces` and your configured separator will be used instead of the default.

## Final words
**gith** is built using **Typer**. Big thanks 🙏 to [Sebastián Ramírez](https://github.com/tiangolo) for creating such amazing tool. 

I hope you find it usefull in your daily work. If you find any bug, or do you have any feedback for new features, feel free to add an issue [here](https://github.com/rejamen/gith/issues). You can also fork, and create PRs if you want to contribute. It would be a pleasure to collaborate 😊