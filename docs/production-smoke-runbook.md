# Production MCP Smoke Runbook

[English](production-smoke-runbook.md) | [Русский](production-smoke-runbook.ru.md)

This runbook describes a safe manual smoke check for the Test IT MCP server on a production Test IT contour. It focuses on MCP `stdio` behavior, tool metadata, argument validation, and preview/apply safety. It does not replace the JetBrains HTTP Client upstream API smoke checks in [http_client/README.md](../http_client/README.md).

## Safety Rules

- Use a low-privilege Test IT token when possible.
- Do not use private production IDs in notes, chats, commits, or screenshots.
- Run read-only and preview checks first.
- Do not run `apply_delete_test_case`, `apply_complete_test_run`, or `apply_unlink_test_cases_from_suite_or_plan` against real production data.
- Run any mutating `apply_*` check only against a disposable production test object created for this smoke and approved for deletion or modification.
- Stop immediately on an unexpected successful mutation, unexpected upstream call during preview, authentication error, or schema-validation bypass.

## Prerequisites

- Local checkout contains the exact build intended for production smoke.
- Environment variables are set locally, not committed:
  - `TESTIT_BASE_URL`
  - `TESTIT_TOKEN`
  - optional `TESTIT_AUTH_TYPE`, default `private_token`
- A non-sensitive smoke record exists with placeholder-safe identifiers:
  - project ID for read checks
  - optional disposable test case ID
  - optional disposable test run ID
  - optional disposable suite or plan ID for link checks

## Safe MCP Smoke Sequence

Start with a local `stdio` run. Replace placeholder IDs only in the terminal session:

```bash
printf '%s\n' \
'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}' \
'{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
'{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_projects","arguments":{"page":1,"pageSize":1}}}' \
'{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"preview_delete_test_case","arguments":{"testCaseId":"replace-disposable-test-case-id"}}}' \
| python3 main.py
```

Expected results:

- `initialize` returns server info and `tools` capability.
- `tools/list` includes base tools and generated `preview_*` / `apply_*` tools for high-impact operations.
- `delete_test_case` has `risk=destructive`, `destructive=true`, `highImpact=true`, and `supportsPreview=true`.
- `preview_delete_test_case` returns `upstream.willCallUpstream=false`, `applyTool=apply_delete_test_case`, target ID, and an `operationId`.
- `list_projects` returns a normalized paginated response or a mapped Test IT authentication/authorization error.

## Negative Safety Checks

Use the `operationId` from the preview response, but intentionally change the target ID:

```bash
printf '%s\n' \
'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}' \
'{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"apply_delete_test_case","arguments":{"testCaseId":"replace-different-test-case-id","operationId":"replace-operation-id-from-preview"}}}' \
'{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"create_test_case","arguments":{"projectId":"replace-project-id","sectionId":"replace-section-id","name":"Smoke","state":"NotReady","priority":"Medium","steps":[{"action":"Open"}],"unexpected":"must-be-rejected"}}}' \
| python3 main.py
```

Expected results:

- Changed `apply_delete_test_case` arguments return `ValidationError` with `field=operationId`.
- Unknown `create_test_case` fields return `ValidationError` with `details.fields=["unexpected"]`.
- No Test IT object is deleted or created by these negative checks.

## Optional Disposable Apply Check

Run this only when a disposable object is explicitly prepared for production smoke:

1. Preview the intended operation and save the returned `operationId` locally.
2. Re-read the target object through a read-only tool.
3. Apply the operation with exactly the same arguments plus `operationId`.
4. Re-read or search the target area to verify only the disposable object changed.
5. Record only sanitized results: tool name, outcome, timestamp, and whether rollback or cleanup was needed.

Preferred disposable apply checks:

- `apply_update_test_case` with a harmless name or description change on a disposable test case.
- `apply_parameterize_test_case` only when disposable parameters and test case data already exist.

Avoid destructive apply checks on production unless the disposable object was created solely for this smoke and deletion is explicitly approved.

## Pass / Fail Criteria

Pass when:

- read-only tools return expected normalized responses;
- tool metadata marks destructive and high-impact tools correctly;
- preview tools do not call mutating upstream endpoints;
- changed `operationId` arguments are rejected;
- unknown write fields are rejected before upstream calls;
- any optional disposable apply affects only the approved disposable object.

Fail when:

- preview appears to mutate data;
- high-impact tools are missing generated preview/apply tools;
- destructive metadata is absent or wrong;
- strict validation accepts unknown write fields;
- `apply_*` accepts arguments different from the previewed arguments;
- any production object outside the disposable smoke scope is changed.

## Handoff Notes

For PR or release handoff, include:

- Test IT contour name as a non-secret label, not a private URL.
- Tool sequence executed.
- Sanitized IDs or aliases only.
- Pass/fail result for each check.
- Confirmation that no destructive apply ran against real production data.
