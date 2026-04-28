# Repo Commit Guide

## Source Priority

Fact: This guide is generated from repository facts: `AGENTS.md`, `README.md`, `pyproject.toml`, current branch, working tree status, recent commit history, and the selected Trunk PR workflow.

Use this priority when sources conflict:

1. Explicit user request for the current commit scope.
2. This `docs/repo-commit-guide.md`.
3. Repository docs such as `AGENTS.md` and `README.md`.
4. Actual staged or unstaged diff.
5. Current branch name.
6. Recent commit history.

Conservative default: The commit message must describe only the diff that will be staged and committed.

## Commit Message Format

Fact: Recent history and `AGENTS.md` use concise imperative commit subjects without a required issue key.

Use:

```text
Verb concise object
```

Examples from this repository:

```text
Rename package to mcp_server
Rename smoke directory to http_client
Add PyCharm Black SDK config
Add initial working Test IT MCP server
```

Prefer specific verbs such as `Add`, `Update`, `Fix`, `Document`, `Remove`, `Rename`, or `Refactor`. Do not add a trailing period.

## Issue Key Rules

Fact: Recent commit history does not show mandatory issue keys.

Conservative default: Do not add an issue key unless the user explicitly provides one or future repository documentation requires one.

## Branch Policy

Fact: The observed current branch during guide creation was `main`.

Fact: The selected GitHub workflow is Trunk PR.

Create short-lived branches from an up-to-date `main` and merge changes back through pull requests. Use branch names such as:

```text
feature/add-agent-guide
fix/config-validation
docs/update-commit-guide
```

Do not commit directly to `main` for normal work. Prefer squash merge so `main` keeps concise, imperative commit subjects.

## Staging Policy

Fact: `AGENTS.md` was the only untracked change observed when this guide was created.

Conservative default: Before staging, inspect `git status --short` and the relevant diff. Stage only files that belong to the user-requested task. Do not stage unrelated local changes.

## Validation Policy

Fact: `README.md` documents the unit test command:

```bash
python3 -m unittest discover -s tests -v
```

Fact: The project is Python 3.12 with no external runtime dependencies in `pyproject.toml`.

Conservative default: Run the unit test command before committing code changes. For documentation-only changes, a readback of edited Markdown is sufficient unless the user asks for tests.

## Missing Facts And Defaults

Conservative default: No documented lint, formatter, coverage threshold, PR template, protected branch rule, or required issue key was found. Do not invent those requirements for commit preparation.

Question: If future work must follow a ticketing or branch naming policy, update this guide before preparing commits that depend on that policy.
