# ai-test-it-mcp

MCP server for Test IT REST API.

The server uses `stdio` JSON-RPC and exposes task-oriented MCP tools for working with:

- projects
- test plans
- test suites
- test cases
- test runs
- test results

## Status

The project is implemented as a lightweight Python 3.12 server with no external runtime dependencies.

The current implementation is aligned to the Swagger contract exposed by:

- `https://ag-pegasus.elocont.ru/swagger/index.html`
- OpenAPI source: `/swagger/v2/swagger.json`

Important API-specific decisions already reflected in code:

- auth header is `Authorization: Bearer <token>`
- test suites are listed by test plan, not by project
- test plans are listed by project
- test runs are listed by project with explicit state flags
- test results are searched through `POST /api/v2/testResults/search`

## Project Layout

- [main.py](main.py): minimal entrypoint
- [ai_test_it_mcp/server.py](ai_test_it_mcp/server.py): MCP tool registration and server bootstrap
- [ai_test_it_mcp/mcp_protocol.py](ai_test_it_mcp/mcp_protocol.py): `stdio` transport and JSON-RPC handling
- [ai_test_it_mcp/testit_client.py](ai_test_it_mcp/testit_client.py): Test IT HTTP client
- [ai_test_it_mcp/services.py](ai_test_it_mcp/services.py): tool-level use cases and argument validation
- [tests/](tests): unit tests
- [http_client/testit-smoke.http](http_client/testit-smoke.http): JetBrains HTTP Client smoke checks for upstream Test IT API

## Requirements

- Python `3.12+`
- access to a Test IT instance
- valid API token

## Configuration

The server reads configuration from environment variables.

Required:

- `TESTIT_BASE_URL`
- `TESTIT_TOKEN`

Optional:

- `TESTIT_TIMEOUT_SECONDS`, default `30`
- `TESTIT_VERIFY_SSL`, default `true`
- `LOG_LEVEL`, default `INFO`

Example:

```bash
export TESTIT_BASE_URL="https://ag-pegasus.elocont.ru"
export TESTIT_TOKEN="your-token"
export TESTIT_TIMEOUT_SECONDS="30"
export TESTIT_VERIFY_SSL="true"
export LOG_LEVEL="INFO"
```

`TESTIT_TOKEN` must contain only the raw token value.  
The server adds the `Bearer` prefix itself.

## Run

Start the server directly:

```bash
python3 main.py
```

Or through the console entrypoint declared in `pyproject.toml`:

```bash
ai-test-it-mcp
```

The process stays attached to `stdin/stdout` and waits for MCP messages.

## MCP Protocol

The server supports:

- `initialize`
- `tools/list`
- `tools/call`

Transport is `stdio` with newline-delimited JSON-RPC messages.

Example request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
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

### List tools

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

### List projects

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

### Get project

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "get_project",
    "arguments": {
      "projectId": "57cf0e1d-7760-493c-9974-9517b314e83f"
    }
  }
}
```

### List test plans

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "list_test_plans",
    "arguments": {
      "projectId": "57cf0e1d-7760-493c-9974-9517b314e83f"
    }
  }
}
```

### List test suites

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

### Search test cases

```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "tools/call",
  "params": {
    "name": "search_test_cases",
    "arguments": {
      "projectId": "57cf0e1d-7760-493c-9974-9517b314e83f",
      "page": 1,
      "pageSize": 20
    }
  }
}
```

### List test runs

```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "tools/call",
  "params": {
    "name": "list_test_runs",
    "arguments": {
      "projectId": "57cf0e1d-7760-493c-9974-9517b314e83f",
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

### List test results

```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "method": "tools/call",
  "params": {
    "name": "list_test_results",
    "arguments": {
      "projectId": "57cf0e1d-7760-493c-9974-9517b314e83f",
      "page": 1,
      "pageSize": 20
    }
  }
}
```

## Error Model

The server maps upstream and local failures to:

- `ConfigurationError`
- `AuthenticationError`
- `AuthorizationError`
- `NotFoundError`
- `ValidationError`
- `RateLimitError`
- `UpstreamError`

Each error includes a short message and may include details such as operation, entity, and HTTP status.

## Tool Catalog

### Projects

- `list_projects`
- `get_project`

### Test Suites

- `list_test_suites`
  Requires `testPlanId`
- `get_test_suite`
- `create_test_suite`
- `update_test_suite`

### Test Plans

- `list_test_plans`
  Requires `projectId`
- `get_test_plan`
- `create_test_plan`
- `update_test_plan`

### Test Cases

- `search_test_cases`
  Uses project-scoped work item listing/search
- `get_test_case`
- `create_test_case`
- `update_test_case`
- `delete_test_case`

### Test Runs

- `list_test_runs`
  Requires `projectId`
  Supports `notStarted`, `inProgress`, `stopped`, `completed`, `testPlanId`, `createdDateFrom`, `createdDateTo`
- `get_test_run`
- `create_test_run`
- `update_test_run`
- `complete_test_run`

### Test Results

- `list_test_results`
  Requires `projectId`
  Uses `POST /api/v2/testResults/search`
- `get_test_result`
- `create_test_result`
- `update_test_result`

### Links

- `link_test_cases_to_suite_or_plan`
- `unlink_test_cases_from_suite_or_plan`

## Notes On API Shape

This server does not blindly mirror all Test IT endpoints.

The MCP surface is normalized for LLM/tool callers, but some upstream API constraints still matter:

- `list_test_suites` cannot work with only `projectId`; it needs `testPlanId`
- `list_test_runs` is not a generic `GET /testRuns`; it is project-scoped and expects state flags
- `list_test_results` is search-based, not a simple collection `GET`
- some list endpoints in Test IT return arrays directly, not paginated envelopes

Because of that, the server wraps upstream array responses into a normalized shape:

```json
{
  "items": [],
  "page": 1,
  "pageSize": 10,
  "total": 0,
  "nextPage": null
}
```

For non-paginated upstream endpoints, `page` and `pageSize` are synthetic and represent the normalized MCP response, not native Test IT pagination.

## Testing

Run unit tests:

```bash
python3 -m unittest discover -s tests -v
```

Current test coverage includes:

- config parsing
- error mapping
- MCP protocol basics
- service-layer validation and request shaping

## Smoke Checks

Use JetBrains HTTP Client files in [http_client/](http_client) to validate the upstream Test IT API assumptions:

- [http_client/testit-smoke.http](http_client/testit-smoke.http)
- [http_client/http-client.env.json](http_client/http-client.env.json)
- `http_client/http-client.private.env.json` for local secrets

These smoke checks validate Test IT endpoints directly, not the MCP `stdio` protocol.

## JetBrains HTTP Client Setup

1. Open `http_client/testit-smoke.http`
2. Select the desired environment from `http_client/http-client.env.json`
3. Keep private secrets in `http_client/http-client.private.env.json`
4. Run requests one by one

Recommended minimum sequence:

1. `List projects`
2. `List test plans`
3. `List test suites` after you have a real `testPlanId`
4. `List test runs`
5. `List test results`

## Limitations

- no attachments support in v1
- no MCP `resources` or `prompts`
- no bulk operations except link/unlink style operations already exposed
- some create/update payloads are passed through with minimal normalization, so callers should stay close to real Test IT field names where required
- the implementation is intentionally lightweight and uses the Python standard library HTTP stack instead of `httpx`

## Development Notes

If you change API routing assumptions, validate them against the live Swagger first.  
The most likely breakages are endpoint shape differences between Test IT deployments.
