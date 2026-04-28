# mcp-server

[English](README.md) | [Русский](README.ru.md)

MCP server for the Test IT REST API.

The server uses `stdio` JSON-RPC and exposes task-oriented MCP tools for working with projects, test plans, test suites, test cases, test runs, and test results.

## Status

The project is implemented as a lightweight Python 3.12 server with no external runtime dependencies.

The current implementation is aligned to a Test IT Swagger contract. Use the Swagger UI and OpenAPI source exposed by your own Test IT instance when validating endpoint assumptions.

Important API-specific decisions already reflected in code:

- auth header is `Authorization: Bearer <token>`
- test suites are listed by test plan, not by project
- test plans are listed by project
- test runs are listed by project with explicit state flags
- test results are searched through `POST /api/v2/testResults/search`

## Quick Start

Requirements:

- Python `3.12+`
- access to a Test IT instance
- valid API token

Configure the environment:

```bash
export TESTIT_BASE_URL="https://testit.example.com"
export TESTIT_TOKEN="your-token"
```

`TESTIT_TOKEN` must contain only the raw token value. The server adds the `Bearer` prefix itself.

Start the server directly:

```bash
python3 main.py
```

Or through the console entrypoint declared in `pyproject.toml`:

```bash
mcp-server
```

The process stays attached to `stdin/stdout` and waits for MCP messages.

## Documentation

- [Documentation index](docs/README.md)
- [Russian documentation index](docs/README.ru.md)
- [Usage and configuration](docs/usage.md)
- [MCP tool catalog](docs/mcp-tools.md)
- [Development notes](docs/development.md)
- [HTTP Client smoke checks](http_client/README.md)

## Project Layout

- [main.py](main.py): minimal entrypoint
- [mcp_server/server.py](mcp_server/server.py): MCP tool registration and server bootstrap
- [mcp_server/mcp_protocol.py](mcp_server/mcp_protocol.py): `stdio` transport and JSON-RPC handling
- [mcp_server/testit_client.py](mcp_server/testit_client.py): Test IT HTTP client
- [mcp_server/services.py](mcp_server/services.py): tool-level use cases and argument validation
- [tests/](tests): unit tests
- [http_client/testit-smoke.http](http_client/testit-smoke.http): JetBrains HTTP Client smoke checks for upstream Test IT API

## Testing

Run the unit test suite:

```bash
python3 -m unittest discover -s tests -v
```
