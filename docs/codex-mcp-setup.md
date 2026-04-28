# Codex MCP Setup

This guide owns local Codex MCP configuration for this repository. It complements [Local Codex workflow](codex-workflow.md) and the tracked template [.codex/config.example.toml](../.codex/config.example.toml).

Use this document when setting up or changing Codex MCP servers. Use [Local Codex workflow](codex-workflow.md) when deciding which tool to use during repository work.

## Configuration File

Codex CLI and the IDE extension share MCP configuration. The standard Codex config path is `~/.codex/config.toml`; this repository also keeps [.codex/config.example.toml](../.codex/config.example.toml) as a project-local template. Copy or merge the template into the config file used by your local Codex launcher:

```bash
cp .codex/config.example.toml .codex/config.toml
```

`.codex/config.toml` is ignored by git for local project-specific configuration. Keep real tokens, private endpoints, private project IDs, and local absolute paths out of tracked files.

After editing MCP configuration, restart or refresh Codex and run `/mcp` in the TUI or inspect the IDE MCP panel. Confirm the expected servers and tools are listed.

## Repository MCP Servers

Use these servers for this project:

| Server | Purpose | Configuration source |
| --- | --- | --- |
| `jetbrains` | IDE-aware navigation, file reads, search, inspections, builds, and refactorings | Local PyCharm installation and IDE MCP port |
| `ai_test_it` | Local stdio MCP server for this repository's Test IT tools | `main.py` plus `TESTIT_*` environment variables |
| `github` | Remote GitHub issues, pull requests, repository metadata, users, and workflow context | GitHub remote MCP server and `GITHUB_PAT_TOKEN` |
| `openaiDeveloperDocs` | Official OpenAI API, Codex, and MCP documentation lookup | OpenAI hosted docs MCP server |

Keep `.codex/config.example.toml` small and runnable as a template. Put workflow policy and tool-selection rules in [Local Codex workflow](codex-workflow.md), not in the config file.

## JetBrains MCP

JetBrains MCP connects Codex to the active IDE. Replace the Java path, classpath entries, and port in the template with values from the local PyCharm installation:

```toml
[mcp_servers.jetbrains]
command = "/path/to/jetbrains/jbr/bin/java"
args = [
  "-classpath",
  "/path/to/pycharm/plugins/mcpserver/lib/mcpserver-frontend.jar:/path/to/pycharm/lib/util-8.jar",
  "com.intellij.mcpserver.stdio.McpStdioRunnerKt",
]

[mcp_servers.jetbrains.env]
IJ_MCP_SERVER_PORT = "64342"
```

Use JetBrains MCP when Codex needs IDE-aware repository context. Keep the server local; do not put machine-specific paths into tracked documentation except as placeholders.

## Test IT MCP

The `ai_test_it` server runs this repository's MCP server over `stdio`:

```toml
[mcp_servers.ai_test_it]
command = "python3"
args = ["-u", "/absolute/path/to/ai-test-it-mcp/main.py"]
startup_timeout_sec = 60

[mcp_servers.ai_test_it.env]
TESTIT_BASE_URL = "https://your-testit.example.com"
TESTIT_TOKEN = "replace-with-token"
TESTIT_TIMEOUT_SECONDS = "30"
TESTIT_VERIFY_SSL = "true"
LOG_LEVEL = "INFO"
```

`TESTIT_TOKEN` must be raw; the server adds `Bearer`. Keep real Test IT tokens and private endpoints only in ignored local config or shell environment.

## GitHub MCP

The GitHub remote MCP server is `https://api.githubcopilot.com/mcp/`. Store the GitHub token in the shell environment before starting Codex:

```bash
export GITHUB_PAT_TOKEN="replace-with-token"
```

Default configuration:

```toml
[mcp_servers.github]
url = "https://api.githubcopilot.com/mcp/"
bearer_token_env_var = "GITHUB_PAT_TOKEN"
```

Equivalent Codex CLI command:

```bash
codex mcp add github --url https://api.githubcopilot.com/mcp/ --bearer-token-env-var GITHUB_PAT_TOKEN
```

Use the narrowest endpoint that fits the work:

| Need | Endpoint |
| --- | --- |
| Default project work | `https://api.githubcopilot.com/mcp/` |
| Read-only project work | `https://api.githubcopilot.com/mcp/readonly` |
| CI inspection only | `https://api.githubcopilot.com/mcp/x/actions/readonly` |
| One read-only toolset | `https://api.githubcopilot.com/mcp/x/{toolset}/readonly` |

Start with least-privilege PAT scopes and expand only when a required tool fails because of permissions. Common scopes are `repo`, `workflow`, and `read:org`; avoid `gist`, `project`, or broader scopes unless a task requires them.

## OpenAI Docs MCP

Use the official OpenAI docs MCP server for OpenAI API, ChatGPT Apps SDK, or Codex documentation questions:

```bash
codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
codex mcp list
```

Prefer official OpenAI documentation over web snippets for OpenAI product behavior.

## References

- [OpenAI Codex MCP docs](https://developers.openai.com/codex/mcp)
- [OpenAI Docs MCP](https://developers.openai.com/learn/docs-mcp)
- [GitHub MCP Codex install guide](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-codex.md)
- [GitHub MCP remote server docs](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md)
