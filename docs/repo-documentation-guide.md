# Repo Documentation Guide

## Source Priority

Fact: This guide is generated from repository facts in `AGENTS.md`, `README.md`, `README.ru.md`, `pyproject.toml`, `docs/README.md`, `docs/README.ru.md`, `docs/usage.md`, `docs/usage.ru.md`, `docs/mcp-tools.md`, `docs/mcp-tools.ru.md`, `docs/development.md`, `docs/development.ru.md`, `docs/repo-commit-guide.md`, `http_client/README.md`, `http_client/README.ru.md`, and the current project source tree.

AI agents must use English documentation as the canonical source. For normal repository work, read one language path per topic: English by default for agents, or Russian for Russian-speaking human readers. Do not read both language counterparts unless the task is translation maintenance, EN/RU synchronization, link validation, or investigation of a suspected mismatch.

Use this priority when sources conflict:

1. Explicit user request for the current documentation task.
2. This `docs/repo-documentation-guide.md`.
3. Repository guidance in `AGENTS.md`.
4. User-facing docs such as `README.md`, `README.ru.md`, `docs/README.md`, `docs/README.ru.md`, `docs/usage.md`, `docs/usage.ru.md`, `docs/mcp-tools.md`, `docs/mcp-tools.ru.md`, `docs/development.md`, `docs/development.ru.md`, `http_client/README.md`, and `http_client/README.ru.md`.
5. Current code, tests, and configuration files.
6. Existing workflow docs under `docs/`.

Conservative default: document current repository behavior only. Do not describe planned architecture as existing behavior.

## Documentation Map

- `README.md`: canonical English user-facing project overview, quick start, top-level navigation, project layout, and test command.
- `README.ru.md`: Russian counterpart to `README.md`.
- `docs/README.md`: canonical English documentation index for user and maintainer docs.
- `docs/README.ru.md`: Russian counterpart to `docs/README.md`.
- `docs/usage.md`: canonical English setup, configuration, run commands, MCP protocol summary, and JSON-RPC examples.
- `docs/usage.ru.md`: Russian counterpart to `docs/usage.md`.
- `docs/mcp-tools.md`: canonical English MCP tool catalog, required arguments, pagination, normalized response shape, and error model.
- `docs/mcp-tools.ru.md`: Russian counterpart to `docs/mcp-tools.md`.
- `docs/development.md`: canonical English maintainer-facing project layout, tests, smoke-check workflow, API-shape notes, limitations, and repository guide links.
- `docs/development.ru.md`: Russian counterpart to `docs/development.md`.
- `http_client/README.md`: canonical English JetBrains HTTP Client smoke-check instructions and upstream Test IT API assumptions.
- `http_client/README.ru.md`: Russian counterpart to `http_client/README.md`.
- `docs/repo-commit-guide.md`: local commit message, staging, branch, and validation workflow.
- `docs/repo-documentation-guide.md`: local documentation workflow, ownership, source priority, verification matrix, and indexing policy.
- `AGENTS.md`: contributor-facing repository guidelines for structure, style, tests, commits, and security.

## Document Ownership

- Runtime entrypoints and packaging facts are owned by `main.py`, `mcp_server/server.py`, and `pyproject.toml`; user-facing run instructions are documented in `README.md`, `README.ru.md`, `docs/usage.md`, and `docs/usage.ru.md`.
- MCP tool names, descriptions, input schemas, and server bootstrap behavior are owned by `mcp_server/server.py`; the public tool catalog is documented in `docs/mcp-tools.md` and `docs/mcp-tools.ru.md`.
- MCP transport, JSON-RPC handling, supported methods, response shape, and protocol framing are owned by `mcp_server/mcp_protocol.py`; user-facing protocol examples are documented in `docs/usage.md` and `docs/usage.ru.md`.
- Test IT HTTP routes, request methods, query/body shaping, authentication header behavior, response extraction, and upstream error handling are owned by `mcp_server/testit_client.py`.
- Tool-level validation, default pagination, required arguments, filters, and use-case orchestration are owned by `mcp_server/services.py`.
- Configuration environment variables, defaults, and parsing rules are owned by `mcp_server/config.py`; user-facing configuration docs live in `docs/usage.md` and `docs/usage.ru.md`.
- Shared response models and pagination shape are owned by `mcp_server/models.py`; public pagination documentation lives in `docs/mcp-tools.md` and `docs/mcp-tools.ru.md`.
- Error categories, payload shape, and HTTP status mapping are owned by `mcp_server/errors.py`; public error documentation lives in `docs/mcp-tools.md` and `docs/mcp-tools.ru.md`.
- Offline unit-test expectations are owned by `tests/`; maintainer-facing test instructions live in `docs/development.md` and `docs/development.ru.md`.
- Manual upstream API smoke-check assumptions are owned by `http_client/testit-smoke.http`, `http_client/README.md`, and `http_client/README.ru.md`; maintainer-facing workflow notes live in `docs/development.md` and `docs/development.ru.md`.

## Verification Matrix

Before changing documentation, verify facts against the relevant sources:

- Project purpose, layout, requirements, setup, and run commands: check `README.md`, `README.ru.md`, `docs/usage.md`, `docs/usage.ru.md`, `AGENTS.md`, `pyproject.toml`, `main.py`, and `mcp_server/server.py`.
- Configuration docs: check `mcp_server/config.py`, `docs/usage.md`, `docs/usage.ru.md`, `README.md`, `README.ru.md`, and `AGENTS.md`.
- MCP protocol docs: check `mcp_server/mcp_protocol.py`, `mcp_server/server.py`, `docs/usage.md`, `docs/usage.ru.md`, and protocol tests in `tests/`.
- MCP tool docs or examples: check `mcp_server/server.py`, `mcp_server/services.py`, `mcp_server/testit_client.py`, `docs/mcp-tools.md`, `docs/mcp-tools.ru.md`, and service/server tests in `tests/`.
- Test IT REST API assumptions: check `mcp_server/testit_client.py`, `http_client/testit-smoke.http`, `http_client/README.md`, `http_client/README.ru.md`, `docs/development.md`, and `docs/development.ru.md`.
- Error behavior: check `mcp_server/errors.py`, `mcp_server/mcp_protocol.py`, `docs/mcp-tools.md`, `docs/mcp-tools.ru.md`, and `tests/test_errors.py`.
- Test instructions and coverage claims: check `AGENTS.md`, `README.md`, `README.ru.md`, `docs/development.md`, `docs/development.ru.md`, `pyproject.toml`, and `tests/`.
- Commit or branch workflow docs: check `docs/repo-commit-guide.md`, `AGENTS.md`, current git state, and recent history when available.

If sources disagree, prefer the higher-priority source and call out the unresolved discrepancy in the final response or in the edited document when it affects readers.

For EN/RU mismatches, English docs win. Fix the Russian counterpart when the task includes documentation edits, or flag the drift if fixing it is out of scope.

## Indexing Policy

Prefer updating the existing owner document for a topic. Create a new document only when no current document owns the topic or when the content would make the owner document hard to use.

Add or update index links only when the document is user-facing or needed for navigation:

- Link from `README.md` to `docs/README.md`, `docs/README.ru.md`, and user-facing setup, usage, protocol, tool, development, or smoke-check docs that readers need outside agent workflows.
- Link from `README.ru.md` to `docs/README.ru.md` and Russian user-facing counterparts.
- Link from `docs/README.md` and `docs/README.ru.md` to user and maintainer documents under `docs/`, plus nearby owner documents such as `http_client/README.md`, `http_client/README.ru.md`, and `AGENTS.md`.
- Link from a nearby owner document when a specialized document extends that document's topic.
- Do not add README links for internal repo guides unless the user asks or discoverability becomes a practical problem.

## Style And Security

- Match the existing concise English Markdown style.
- English user-facing docs are canonical for maintainers and AI agents. Russian user-facing docs use the `.ru.md` suffix and preserve the same factual meaning, examples, commands, environment variables, JSON fields, tool names, and file paths.
- A reader should use either the English doc or the Russian counterpart for normal usage, not both. AI agents should choose English by default.
- Add language switch links near the top of paired user-facing documents in the form `English | Русский`.
- Create new user-facing docs as English/Russian pairs unless the document is explicitly internal-only.
- Use concrete file paths for source-backed statements.
- Keep examples small and directly runnable when possible.
- Separate verified facts from assumptions.
- Do not include real Test IT tokens, private endpoint credentials, or private environment values.
- Do not include private company names, private hostnames, private project IDs, or real UUIDs in either language.
- Preserve the documented behavior that `TESTIT_TOKEN` is raw, `TESTIT_AUTH_TYPE` controls the prefix, and `private_token` is the default.

## Completion Criteria

A documentation task is complete when:

1. The existing owner document for the topic has been found or a new owner document has a clear reason to exist.
2. Claims have been checked against the verification matrix for that topic.
3. New or changed links point to existing paths.
4. Markdown has been read back for obvious formatting issues.
5. Tests or commands are run only when they are relevant to the documentation change; for docs-only edits, readback is sufficient unless the user asks for more validation.
6. The final response lists changed documents, checked sources, indexing changes, and remaining assumptions.
