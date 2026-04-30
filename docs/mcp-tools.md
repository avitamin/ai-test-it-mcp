# MCP Tool Catalog

[English](mcp-tools.md) | [Русский](mcp-tools.ru.md)

The MCP tool registry is defined in `mcp_server/server.py`. Tool-level validation and request shaping are implemented in `mcp_server/services.py`.

## Safety And Transparency

`tools/list` descriptors include `annotations` and `metadata` that identify read-only, write, destructive, high-impact, and preview-capable tools. The server validates tool arguments against the declared input schema before calling service handlers. Unknown fields are rejected for closed schemas instead of being silently sent to Test IT.

Write tools use explicit allowlists for upstream payloads. They no longer provide a general-purpose pass-through channel for arbitrary Test IT fields.

Successful write calls return a standard envelope with `operation`, `target`, `changedFields`, `risk`, `success`, and the original service result in `result`.

High-impact tools also expose generated two-phase tools:

- `preview_<toolName>` validates the same arguments and returns `operationId`, `expiresAt`, `target`, `changedFields`, risk metadata, and the matching apply tool name. It does not call a mutating upstream endpoint.
- `apply_<toolName>` requires the original arguments plus `operationId`. The server rejects expired IDs or IDs that do not match the supplied arguments.

Preview operation IDs expire after 10 minutes.

Preview-capable tools are:

- `update_test_case`
- `delete_test_case`
- `replace_test_case_steps_with_shared_step`
- `extract_shared_step_from_test_case_steps`
- `parameterize_test_case`
- `complete_test_run`
- `unlink_test_cases_from_suite_or_plan`

## Pagination And Responses

Paginated tools use:

- `page`, default `1`
- `pageSize`, default `20`, allowed range `1..100`

The server normalizes upstream list responses into:

```json
{
  "items": [],
  "page": 1,
  "pageSize": 20,
  "total": 0,
  "nextPage": null
}
```

For non-paginated upstream endpoints, `page` and `pageSize` are synthetic and represent the normalized MCP response, not native Test IT pagination.

## Projects

- `list_projects`: optional `page`, `pageSize`
- `get_project`: required `projectId`

## Test Suites

- `list_test_suites`: required `testPlanId`
- `get_test_suite`: required `testSuiteId`
- `create_test_suite`: required `projectId`, `name`; optional `description`
- `update_test_suite`: required `testSuiteId`; optional `name`, `description`

`list_test_suites` is test-plan scoped and cannot work with only `projectId`.

## Test Plans

- `list_test_plans`: required `projectId`; optional `includeDeleted`
- `get_test_plan`: required `testPlanId`
- `create_test_plan`: required `projectId`, `name`; optional `description`
- `update_test_plan`: required `testPlanId`; optional `name`, `description`

## Test Cases

- `search_test_cases`: required `projectId`; optional `page`, `pageSize`, `search`, `includeDeleted`, `OrderBy`, `SearchField`, `SearchValue`
- `get_test_case`: required `testCaseId`
- `create_test_case`: required `projectId`, `sectionId`, `name`, `state`, `priority`, non-empty `steps`; defaults `entityTypeName` to `TestCases`, `duration` to `600000`, and empty `tags`, `links`, `attributes`, `preconditionSteps`, `postconditionSteps`
- `update_test_case`: required `testCaseId`; accepts explicit work item fields only and supports preview/apply
- `delete_test_case`: required `testCaseId`
- `get_test_case_steps`: required `testCaseId`
- `parameterize_test_case`: required `testCaseId`, `projectId`, and exactly one of `parameters` or `iterations`; optional `replacements`

Test cases use Test IT work item endpoints upstream. `search_test_cases` uses `POST /api/v2/projects/{projectId}/workItems/search` with `filter.types=["TestCases"]`.

`get_test_case_steps` normalizes step fields and returns upstream `iterations` from the fetched work item. `parameterize_test_case` only reuses existing Test IT parameters: it searches parameters by `projectId`, `name`, and `value`, writes matching IDs to work item `iterations`, and updates matching step text with `{{parameterName}}`. It does not create or update parameter dictionary entries.

Step selectors use exactly one of:

- `stepIds`: upstream step IDs
- `stepIndexes`: 1-based step positions in the current test case

## Shared Steps

- `search_shared_steps`: required `projectId`; optional `page`, `pageSize`, `search`, `OrderBy`, `SearchField`, `SearchValue`
- `create_shared_step`: required `projectId`, `sectionId`, `name`, `state`, `priority`, non-empty `steps`; defaults `entityTypeName` to `SharedSteps`, `duration` to `0`, and empty `tags`, `links`, `attributes`, `preconditionSteps`, `postconditionSteps`
- `replace_test_case_steps_with_shared_step`: required `testCaseId`, `sharedStepId`; plus exactly one of `stepIds` or `stepIndexes`; optional `parameterValues`; supports preview/apply
- `extract_shared_step_from_test_case_steps`: required `testCaseId`, `projectId`, `sectionId`, `name`, `state`, `priority`; plus exactly one of `stepIds` or `stepIndexes`; optional `parameterValues`, `entityTypeName`; supports preview/apply

Shared step tools use Test IT work item endpoints upstream. Shared-step references are represented in Test IT steps by `workItemId`. Replacement tools fetch the current test case, update only its step list, and send the sanitized update model back through `PUT /api/v2/workItems`.

## Test Runs

- `list_test_runs`: required `projectId`; optional `page`, `pageSize`, `testPlanId`, `notStarted`, `inProgress`, `stopped`, `completed`, `createdDateFrom`, `createdDateTo`, `OrderBy`, `SearchField`, `SearchValue`
- `get_test_run`: required `testRunId`
- `create_test_run`: required `projectId`, `name`; optional `description`, `testPlanId`
- `update_test_run`: required `testRunId`; optional `name`, `description`, `testPlanId`
- `complete_test_run`: required `testRunId`; supports preview/apply

If state flags are omitted, `list_test_runs` sends all four state flags as true.

## Test Results

- `list_test_results`: required `projectId`; optional `testRunId`, `testCaseId`, `page`, `pageSize`, `OrderBy`, `SearchField`, `SearchValue`
- `get_test_result`: required `testResultId`
- `create_test_result`: required `projectId`; optional `testRunId`, `testCaseId`, `outcome`, `comment`, `duration`
- `update_test_result`: required `testResultId`; optional `testRunId`, `testCaseId`, `outcome`, `comment`, `duration`

`list_test_results` uses `POST /api/v2/testResults/search`. The service sends `projectIds` and maps `testCaseId` to upstream `workItemIds`.

## Links

- `link_test_cases_to_suite_or_plan`: required `parentType`, `parentId`, `testCaseIds`
- `unlink_test_cases_from_suite_or_plan`: required `parentType`, `parentId`, `testCaseIds`; supports preview/apply

`parentType` must be either `test_suite` or `test_plan`.

## Error Model

The server maps upstream and local failures to:

- `ConfigurationError`
- `AuthenticationError`
- `AuthorizationError`
- `NotFoundError`
- `ValidationError`
- `RateLimitError`
- `UpstreamError`

Each error includes a short message and may include details such as operation, entity, field, and HTTP status.
