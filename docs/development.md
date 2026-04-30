# Development Notes

[English](development.md) | [Русский](development.ru.md)

## Project Layout

- `main.py`: minimal local entrypoint
- `mcp_server/server.py`: MCP tool registration and server bootstrap
- `mcp_server/mcp_protocol.py`: `stdio` transport and JSON-RPC handling
- `mcp_server/testit_client.py`: Test IT HTTP client
- `mcp_server/services.py`: tool-level use cases and argument validation
- `mcp_server/config.py`: environment configuration parsing
- `mcp_server/models.py`: shared response and pagination models
- `mcp_server/errors.py`: error categories and HTTP status mapping
- `tests/`: offline unit tests
- `http_client/`: JetBrains HTTP Client smoke checks for upstream Test IT API assumptions

## Testing

Run the full unit test suite:

```bash
python3 -m unittest discover -s tests -v
```

Current test coverage includes:

- config parsing
- error mapping
- MCP protocol basics
- MCP argument schema validation and preview/apply guards
- service-layer validation and request shaping

Tests use the standard library `unittest`. Keep tests offline with small fake clients or mocks.

## Smoke Checks

Use JetBrains HTTP Client files in [http_client/](../http_client/) to validate the upstream Test IT API assumptions:

- [http_client/testit-smoke.http](../http_client/testit-smoke.http)
- [http_client/http-client.env.json](../http_client/http-client.env.json)
- `http_client/http-client.private.env.json` for local secrets

Recommended minimum sequence:

1. `List projects`
2. `List test plans`
3. `List test suites` after you have a real `testPlanId`
4. `List test runs`
5. `List test results`

These smoke checks validate Test IT endpoints directly, not the MCP `stdio` protocol. JetBrains HTTP Client speaks HTTP, while this MCP server currently uses `stdio` JSON-RPC.

## API Shape Notes

This server does not blindly mirror all Test IT endpoints.

This server version targets the Pegasus/Test IT API v2 contract. Keep a local OpenAPI cache at `.local/swagger-v2.json` for endpoint and schema checks. The `.local/` directory is ignored and should not be committed.

The MCP surface is normalized for LLM/tool callers, but some upstream API constraints still matter:

- `list_test_suites` needs `testPlanId`
- `list_test_runs` is project-scoped and expects state flags
- `list_test_results` is search-based, not a simple collection `GET`
- some list endpoints in Test IT return arrays directly, not paginated envelopes
- write tools use explicit allowlists instead of arbitrary Test IT payload pass-through
- high-impact write tools should expose preview/apply coverage and tests

If you change API routing assumptions, validate them against the cached v2 contract first. The most likely breakages are endpoint shape differences between Test IT deployments.

## Limitations

- no attachments support in v1
- no MCP `resources` or `prompts`
- no bulk operations except link/unlink style operations already exposed
- write payload coverage is intentionally narrower than the upstream Test IT API
- the implementation is intentionally lightweight and uses the Python standard library HTTP stack instead of `httpx`

## Repository Guides

- [Local Codex workflow](codex-workflow.md)
