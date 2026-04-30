# Usage And Configuration

[English](usage.md) | [Русский](usage.ru.md)

## Requirements

- Python `3.12+`
- access to a Test IT instance
- valid API token

The package has no external runtime dependencies.

## Configuration

The server reads configuration from environment variables.

Required:

- `TESTIT_BASE_URL`
- `TESTIT_TOKEN`

Optional:

- `TESTIT_AUTH_TYPE`, default `private_token`; supported values are `private_token` and `bearer`
- `TESTIT_TIMEOUT_SECONDS`, default `30`
- `TESTIT_VERIFY_SSL`, default `true`
- `LOG_LEVEL`, default `INFO`

Example:

```bash
export TESTIT_BASE_URL="https://testit.example.com"
export TESTIT_TOKEN="your-token"
export TESTIT_AUTH_TYPE="private_token"
export TESTIT_TIMEOUT_SECONDS="30"
export TESTIT_VERIFY_SSL="true"
export LOG_LEVEL="INFO"
```

`TESTIT_TOKEN` must contain only the raw token value. The server adds the authorization prefix itself. By default it sends `Authorization: PrivateToken <token>` for Test IT private API tokens documented as `PrivateToken {API Secret Key}`. Use `TESTIT_AUTH_TYPE=bearer` to send `Authorization: Bearer <token>` only when a Bearer token is intentionally needed.

Boolean values such as `TESTIT_VERIFY_SSL` accept `1`, `true`, `yes`, and `on` for true, or `0`, `false`, `no`, and `off` for false.

## Run

Start the server directly:

```bash
python3 main.py
```

Or through the console entrypoint declared in `pyproject.toml` after installing the package:

```bash
mcp-server
```

For editable installs, use a virtual environment and run:

```bash
python3 -m pip install -e .
```

The process stays attached to `stdin/stdout` and waits for MCP messages.

## MCP Protocol

The server supports:

- `initialize`
- `tools/list`
- `tools/call`

Transport is `stdio` with newline-delimited JSON-RPC messages.

Successful tool responses include:

- `content`
- `structuredContent`
- `isError: false`

Failures are returned as JSON-RPC errors with normalized error codes in `error.data.code`.

## Examples

### Initialize

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {}
}
```

### List Tools

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

### List Projects

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "list_projects",
    "arguments": {
      "page": 1,
      "pageSize": 10
    }
  }
}
```

### Get Project

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "get_project",
    "arguments": {
      "projectId": "replace-project-id"
    }
  }
}
```

### List Test Plans

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "list_test_plans",
    "arguments": {
      "projectId": "replace-project-id"
    }
  }
}
```

### List Test Suites

`list_test_suites` requires `testPlanId`, not `projectId`.

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "list_test_suites",
    "arguments": {
      "testPlanId": "replace-test-plan-id"
    }
  }
}
```

### Search Test Cases

```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "search_test_cases",
    "arguments": {
      "projectId": "replace-project-id",
      "page": 1,
      "pageSize": 20
    }
  }
}
```

### Extract Shared Step From Test Case Steps

`stepIndexes` are 1-based positions in the current test case. Use `stepIds` instead when upstream step IDs are known.

```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tools/call",
  "params": {
    "name": "extract_shared_step_from_test_case_steps",
    "arguments": {
      "projectId": "replace-project-id",
      "sectionId": "replace-section-id",
      "testCaseId": "replace-test-case-id",
      "name": "Reusable login",
      "state": "NotReady",
      "priority": "Medium",
      "stepIndexes": [1, 2, 3]
    }
  }
}
```

### Replace Test Case Steps With Shared Step

```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "method": "tools/call",
  "params": {
    "name": "replace_test_case_steps_with_shared_step",
    "arguments": {
      "testCaseId": "replace-test-case-id",
      "sharedStepId": "replace-shared-step-id",
      "stepIds": ["replace-step-id"]
    }
  }
}
```

### Parameterize Test Case

```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "method": "tools/call",
  "params": {
    "name": "parameterize_test_case",
    "arguments": {
      "testCaseId": "replace-test-case-id",
      "parameters": [
        {"name": "user", "value": "admin"}
      ],
      "replacements": [
        {"value": "admin", "parameterName": "user"}
      ]
    }
  }
}
```

### List Test Runs

```json
{
  "jsonrpc": "2.0",
  "id": 11,
  "method": "tools/call",
  "params": {
    "name": "list_test_runs",
    "arguments": {
      "projectId": "replace-project-id",
      "page": 1,
      "pageSize": 20,
      "notStarted": true,
      "inProgress": true,
      "stopped": true,
      "completed": true
    }
  }
}
```

### List Test Results

```json
{
  "jsonrpc": "2.0",
  "id": 12,
  "method": "tools/call",
  "params": {
    "name": "list_test_results",
    "arguments": {
      "projectId": "replace-project-id",
      "page": 1,
      "pageSize": 20
    }
  }
}
```
