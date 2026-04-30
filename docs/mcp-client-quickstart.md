# MCP Client Quick Start

[English](mcp-client-quickstart.md) | [Русский](mcp-client-quickstart.ru.md)

Use this guide to connect this Test IT MCP server to Codex or Claude Code as a local `stdio` MCP server.

## Prerequisites

- Python `3.12+`
- local checkout of this repository
- access to a Test IT instance
- valid Test IT API token

Use the absolute path to this repository when configuring a client:

```bash
pwd
```

The examples below use `/absolute/path/to/ai-test-it-mcp/main.py` as a placeholder. Replace it with the real path on your machine.

`TESTIT_TOKEN` must contain only the raw token value. The server adds the authorization prefix itself; the default is `PrivateToken`.

## Codex

Codex supports MCP servers in the CLI and IDE extension. The clients share MCP configuration, so configuring the server once makes it available in both.

Add the local Test IT MCP server:

```bash
codex mcp add ai_test_it \
  --env TESTIT_BASE_URL=https://testit.example.com \
  --env TESTIT_TOKEN=replace-with-token \
  --env TESTIT_TIMEOUT_SECONDS=30 \
  --env TESTIT_VERIFY_SSL=true \
  --env LOG_LEVEL=INFO \
  -- python3 -u /absolute/path/to/ai-test-it-mcp/main.py
```

Verify the server is configured:

```bash
codex mcp list
```

In the Codex TUI, use:

```text
/mcp
```

## Claude Code

Claude Code supports local `stdio` MCP servers through `claude mcp add`. Options such as `--transport`, `--env`, and `--scope` must come before the server name. The `--` separator marks the command that starts the MCP server.

Add the local Test IT MCP server:

```bash
claude mcp add --transport stdio \
  --env TESTIT_BASE_URL=https://testit.example.com \
  --env TESTIT_TOKEN=replace-with-token \
  --env TESTIT_TIMEOUT_SECONDS=30 \
  --env TESTIT_VERIFY_SSL=true \
  --env LOG_LEVEL=INFO \
  ai_test_it -- python3 -u /absolute/path/to/ai-test-it-mcp/main.py
```

Verify the server is configured:

```bash
claude mcp list
```

Inside Claude Code, check server status with:

```text
/mcp
```

## Troubleshooting

- If the server does not start, confirm the `main.py` path is absolute and exists.
- If tools are missing, restart or refresh the client and check `/mcp`.
- If startup times out, increase the client's MCP startup timeout.
- If authentication fails, confirm `TESTIT_BASE_URL` points to your Test IT instance, `TESTIT_TOKEN` is raw without an authorization prefix, and `TESTIT_AUTH_TYPE` matches the token type.
- If SSL verification fails for a local or private instance, set `TESTIT_VERIFY_SSL=false` only when that is acceptable for your environment.

## References

- [OpenAI Codex MCP docs](https://developers.openai.com/codex/mcp)
- [OpenAI Docs MCP quickstart](https://developers.openai.com/learn/docs-mcp)
- [Claude Code MCP docs](https://code.claude.com/docs/en/mcp)
