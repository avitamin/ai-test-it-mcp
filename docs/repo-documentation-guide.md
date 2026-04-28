# Repo Documentation Guide

## Source Priority

Fact: This guide is generated from repository facts in `AGENTS.md`, `README.md`, `pyproject.toml`, `docs/repo-commit-guide.md`, `http_client/README.md`, and the current project source tree.

Use this priority when sources conflict:

1. Explicit user request for the current documentation task.
2. This `docs/repo-documentation-guide.md`.
3. Repository guidance in `AGENTS.md`.
4. User-facing docs such as `README.md` and `http_client/README.md`.
5. Current code, tests, and configuration files.
6. Existing workflow docs under `docs/`.

Conservative default: document current repository behavior only. Do not describe planned architecture as existing behavior.

## Documentation Map

- `README.md`: main user-facing project overview, setup, configuration, run commands, MCP protocol summary, and examples.
- `http_client/README.md`: JetBrains HTTP Client smoke-check instructions and upstream Test IT API assumptions.
- `docs/repo-commit-guide.md`: local commit message, staging, branch, and validation workflow.
- `docs/repo-documentation-guide.md`: local documentation workflow, ownership, source priority, verification matrix, and indexing policy.
- `AGENTS.md`: contributor-facing repository guidelines for structure, style, tests, commits, and security.

## Document Ownership

- Runtime entrypoints and packaging facts are owned by `main.py`, `mcp_server/server.py`, and `pyproject.toml`.
- MCP tool names, descriptions, input schemas, and server bootstrap behavior are owned by `mcp_server/server.py`.
- MCP transport, JSON-RPC handling, supported methods, response shape, and protocol framing are owned by `mcp_server/mcp_protocol.py`.
- Test IT HTTP routes, request methods, query/body shaping, authentication header behavior, response extraction, and upstream error handling are owned by `mcp_server/testit_client.py`.
- Tool-level validation, default pagination, required arguments, filters, and use-case orchestration are owned by `mcp_server/services.py`.
- Configuration environment variables, defaults, and parsing rules are owned by `mcp_server/config.py`.
- Shared response models and pagination shape are owned by `mcp_server/models.py`.
- Error categories, payload shape, and HTTP status mapping are owned by `mcp_server/errors.py`.
- Offline unit-test expectations are owned by `tests/`.
- Manual upstream API smoke-check assumptions are owned by `http_client/testit-smoke.http` and `http_client/README.md`.

## Verification Matrix

Before changing documentation, verify facts against the relevant sources:

- Project purpose, layout, requirements, setup, and run commands: check `README.md`, `AGENTS.md`, `pyproject.toml`, `main.py`, and `mcp_server/server.py`.
- Configuration docs: check `mcp_server/config.py`, `README.md`, and `AGENTS.md`.
- MCP protocol docs: check `mcp_server/mcp_protocol.py`, `mcp_server/server.py`, and protocol tests in `tests/`.
- MCP tool docs or examples: check `mcp_server/server.py`, `mcp_server/services.py`, `mcp_server/testit_client.py`, and service/server tests in `tests/`.
- Test IT REST API assumptions: check `mcp_server/testit_client.py`, `http_client/testit-smoke.http`, and `http_client/README.md`.
- Error behavior: check `mcp_server/errors.py`, `mcp_server/mcp_protocol.py`, and `tests/test_errors.py`.
- Test instructions and coverage claims: check `AGENTS.md`, `README.md`, `pyproject.toml`, and `tests/`.
- Commit or branch workflow docs: check `docs/repo-commit-guide.md`, `AGENTS.md`, current git state, and recent history when available.

If sources disagree, prefer the higher-priority source and call out the unresolved discrepancy in the final response or in the edited document when it affects readers.

## Indexing Policy

Prefer updating the existing owner document for a topic. Create a new document only when no current document owns the topic or when the content would make the owner document hard to use.

Add or update index links only when the document is user-facing or needed for navigation:

- Link from `README.md` for user-facing setup, usage, protocol, or workflow docs that readers need outside agent workflows.
- Link from a nearby owner document when a specialized document extends that document's topic.
- Do not add README links for internal repo guides unless the user asks or discoverability becomes a practical problem.

## Style And Security

- Match the existing concise English Markdown style.
- Use concrete file paths for source-backed statements.
- Keep examples small and directly runnable when possible.
- Separate verified facts from assumptions.
- Do not include real Test IT tokens, private endpoint credentials, or private environment values.
- Preserve the documented behavior that `TESTIT_TOKEN` is raw and the server adds the `Bearer` prefix.

## Completion Criteria

A documentation task is complete when:

1. The existing owner document for the topic has been found or a new owner document has a clear reason to exist.
2. Claims have been checked against the verification matrix for that topic.
3. New or changed links point to existing paths.
4. Markdown has been read back for obvious formatting issues.
5. Tests or commands are run only when they are relevant to the documentation change; for docs-only edits, readback is sufficient unless the user asks for more validation.
6. The final response lists changed documents, checked sources, indexing changes, and remaining assumptions.
