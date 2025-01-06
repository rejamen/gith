# gith

A Typer-based CLI helper for Git operations.

## Installation

```bash
pip install gith
```

## Usage

### List local branches

```bash
gith branch --list
```

### Create a new branch

```bash
gith branch --create new_branch_name
```

### Create a new branch from a specific branch

```bash
gith branch --create new_branch_name --from 2
```

### Delete branches by their indexes

```bash
gith branch --delete 1,3,5
```

### Keep specific branches and delete the rest

```bash
gith branch --keep 2,4
```

### Checkout to a branch by its index

```bash
gith checkout 2
```