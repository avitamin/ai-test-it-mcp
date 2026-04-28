# mcp-server

[English](README.md) | [Русский](README.ru.md)

MCP server for the Test IT REST API. It runs over `stdio` JSON-RPC and exposes MCP tools for projects, test plans, test suites, test cases, test runs, test results, and links between cases and suites or plans.

The project is a lightweight Python 3.12 server with no external runtime dependencies.

## Requirements

- Python `3.12+`
- access to a Test IT instance
- valid Test IT API token

## Quick Start

Most users connect this server to an MCP client such as Codex or Claude Code. The client starts the server process and communicates with it over `stdio`.

Use the client setup guide:

- [Codex and Claude Code quick start](docs/mcp-client-quickstart.md)

You will need these Test IT values when configuring the client:

```bash
export TESTIT_BASE_URL="https://testit.example.com"
export TESTIT_TOKEN="your-token"
```

`TESTIT_TOKEN` must contain only the raw token value. The server adds the `Bearer` prefix itself.

## Run Directly

Direct startup is useful for local checks, development, and protocol debugging.

Start the server from the repository:

```bash
python3 main.py
```

Or install the package in editable mode and use the console entrypoint:

```bash
python3 -m pip install -e .
mcp-server
```

The process stays attached to `stdin/stdout` and waits for MCP messages.

## What You Can Do

The tool set covers common Test IT workflows:

- list and fetch projects
- list, create, update, and fetch test plans and test suites
- search, create, update, fetch, and delete test cases
- list, create, update, fetch, and complete test runs
- list, create, update, and fetch test results
- link or unlink test cases to a test suite or test plan

See [MCP tool catalog](docs/mcp-tools.md) for required arguments, pagination, response shape, and error behavior.

## API Notes

The implementation follows assumptions validated against a Test IT Swagger contract. Use the Swagger UI and OpenAPI source exposed by your own Test IT instance when checking endpoint behavior.

Notable behavior:

- test suites are listed by test plan, not by project
- test plans and test runs are listed by project
- test results are searched through `POST /api/v2/testResults/search`

## Where To Go Next

- [Documentation index](docs/README.md)
- [Codex and Claude Code quick start](docs/mcp-client-quickstart.md)
- [Usage and configuration](docs/usage.md)
- [MCP tool catalog](docs/mcp-tools.md)
- [Development notes](docs/development.md)
- [HTTP Client smoke checks](http_client/README.md)
- [Russian documentation index](docs/README.ru.md)

## Project Layout

- [main.py](main.py): minimal entrypoint
- [mcp_server/server.py](mcp_server/server.py): MCP tool registration and server bootstrap
- [mcp_server/mcp_protocol.py](mcp_server/mcp_protocol.py): `stdio` transport and JSON-RPC handling
- [mcp_server/testit_client.py](mcp_server/testit_client.py): Test IT HTTP client
- [mcp_server/services.py](mcp_server/services.py): tool-level use cases and argument validation
- [tests/](tests): unit tests
- [http_client/testit-smoke.http](http_client/testit-smoke.http): JetBrains HTTP Client smoke checks

## Testing

Run the unit test suite:

```bash
python3 -m unittest discover -s tests -v
```
