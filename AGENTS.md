# Repository Guidelines

## Project Structure & Module Organization

This repository is a Python 3.12 MCP server for the Test IT REST API.

- `main.py`: minimal local entrypoint.
- `mcp_server/`: server implementation.
  - `server.py`: MCP tool registration and bootstrap.
  - `mcp_protocol.py`: stdio JSON-RPC transport and protocol handling.
  - `testit_client.py`: Test IT HTTP client.
  - `services.py`: tool-level validation and use cases.
  - `config.py`, `models.py`, `errors.py`: configuration, data models, and error mapping.
- `tests/`: unit tests for configuration, services, protocol, and errors.
- `http_client/`: JetBrains HTTP Client smoke checks for upstream Test IT API assumptions.

## Build, Test, and Development Commands

- `python3 main.py`: run the MCP server directly over `stdin/stdout`.
- `mcp-server`: run the console script declared in `pyproject.toml` after installing the package.
- `python3 -m unittest discover -s tests -v`: run the full unit test suite.
- JetBrains HTTP smoke checks: fill `http_client/http-client.env.json`, open `http_client/testit-smoke.http`, select `local`, and run requests one by one.

For editable installs, use a virtual environment and run `python3 -m pip install -e .`.

## Coding Style & Naming Conventions

Use Python 3.12 features when they keep the code clear. Follow the existing style: 4-space indentation, type hints where useful, and `from __future__ import annotations` in Python modules. Prefer explicit validation and small functions.

Name modules with `snake_case.py`, classes with `PascalCase`, functions and variables with `snake_case`, and constants or environment keys with `UPPER_SNAKE_CASE`.

## Testing Guidelines

Tests use the standard library `unittest`, not pytest. Place tests in `tests/test_*.py`, group them in `unittest.TestCase` classes, and name methods `test_<behavior>`. Use small fake clients or mocks to keep tests offline. Add or update tests when changing protocol behavior, request shaping, validation, configuration parsing, or error mapping.

## AI Agent Tooling Priority

AI agents should prefer JetBrains MCP tools for IDE-aware repository work, including project navigation, file reads, code search, inspections, builds, run configurations, and refactorings. Use shell tools only when JetBrains MCP cannot perform the task directly or when a plain terminal command is the correct interface.

For Codex-specific workflow, MCP selection, validation, and PR handoff guidance, use `docs/codex-workflow.md`. For local MCP server configuration, use `docs/codex-mcp-setup.md`.

Additional context for AI agents:

- Use `docs/codex-workflow.md` for Codex task flow, validation, and MCP usage decisions.
- Use the concrete owner document for the topic, such as `docs/usage.md`, `docs/mcp-tools.md`, `docs/development.md`, or `http_client/README.md`.
- Load code, tests, and English canonical docs needed for the specific task.

## Documentation Language Policy

English documentation is the canonical source for repository work and AI agents. Agents should read English docs by default. If an agent has already read an English document for a task, it should not read the Russian `.ru.md` counterpart for the same task.

Russian `.ru.md` files are translation counterparts for Russian-speaking readers. A reader should use either the English document or the Russian counterpart for normal usage, not both. Read both only when maintaining translations, validating EN/RU synchronization, or investigating a suspected mismatch. If English and Russian docs conflict, follow English and fix or flag the Russian drift.

## Documentation After Feature Changes

After implementing a feature or behavior change, AI agents must perform an impact-based documentation check before handoff. Update documentation when the change affects public MCP tools, setup or configuration, runtime behavior, validation rules, error behavior, tests, smoke checks, or maintainer workflow.

Use the concrete owner document for the affected behavior: `docs/mcp-tools.md` for public MCP tools and error behavior, `docs/usage.md` for setup and runtime behavior, `docs/development.md` for tests or maintainer workflow, and `http_client/README.md` for smoke checks. Update canonical English docs first, and update Russian `.ru.md` counterparts when the changed document has one. If no documentation changes are needed, state that explicitly in the final response with the sources checked.

## Commit & Pull Request Guidelines

Recent history uses concise imperative commits, for example `Rename package to mcp_server` and `Add initial working Test IT MCP server`. Keep subjects short and focused on one change.

Use short branches from `main`, such as `feature/add-agent-guide`, `fix/config-validation`, or `docs/update-commit-guide`. Open pull requests for changes and prefer squash merge so `main` keeps a concise history.

Pull requests should include a summary, reason for the change, test results such as `python3 -m unittest discover -s tests -v`, and any configuration or API-contract impact. Link related issues when available.

## Security & Configuration Tips

Do not commit real Test IT tokens or private endpoint credentials. The server reads `TESTIT_BASE_URL`, `TESTIT_TOKEN`, `TESTIT_TIMEOUT_SECONDS`, `TESTIT_VERIFY_SSL`, and `LOG_LEVEL` from the environment. `TESTIT_TOKEN` must be raw; the server adds `Bearer`.
