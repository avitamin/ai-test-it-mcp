# MCP Tool Catalog

[English](mcp-tools.md) | [Русский](mcp-tools.ru.md)

The MCP tool registry is defined in `mcp_server/server.py`. Tool-level validation and request shaping are implemented in `mcp_server/services.py`.

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
- `create_test_suite`: required `projectId`, `name`; additional Test IT fields are passed through
- `update_test_suite`: required `testSuiteId`; additional Test IT fields are passed through

`list_test_suites` is test-plan scoped and cannot work with only `projectId`.

## Test Plans

- `list_test_plans`: required `projectId`; optional `includeDeleted`
- `get_test_plan`: required `testPlanId`
- `create_test_plan`: required `projectId`, `name`; additional Test IT fields are passed through
- `update_test_plan`: required `testPlanId`; additional Test IT fields are passed through

## Test Cases

- `search_test_cases`: required `projectId`; optional `page`, `pageSize`, `search`, `includeDeleted`, `OrderBy`, `SearchField`, `SearchValue`
- `get_test_case`: required `testCaseId`
- `create_test_case`: required `projectId`, `sectionId`, `name`, `state`, `priority`, `steps`; defaults `entityTypeName` to `TestCases`, `duration` to `600000`, and empty `tags`, `links`, `attributes`, `preconditionSteps`, `postconditionSteps`
- `update_test_case`: required `testCaseId`; full Test IT update fields are passed through to `PUT /api/v2/workItems`
- `delete_test_case`: required `testCaseId`
- `get_test_case_steps`: required `testCaseId`
- `parameterize_test_case`: required `testCaseId`, `parameters`; optional `replacements`, `allowParameterOverwrite`

Test cases use Test IT work item endpoints upstream. `search_test_cases` uses `POST /api/v2/projects/{projectId}/workItems/search` with `filter.types=["TestCases"]`.

`get_test_case_steps` normalizes step and parameter fields from the fetched work item. `parameterize_test_case` updates matching step text with `{{parameterName}}`; Test IT parameter set persistence is represented upstream by iterations and is not expanded by this tool yet.

Step selectors use exactly one of:

- `stepIds`: upstream step IDs
- `stepIndexes`: 1-based step positions in the current test case

## Shared Steps

- `search_shared_steps`: required `projectId`; optional `page`, `pageSize`, `search`, `OrderBy`, `SearchField`, `SearchValue`
- `create_shared_step`: required `projectId`, `sectionId`, `name`, `state`, `priority`, `steps`; defaults `entityTypeName` to `SharedSteps`, `duration` to `0`, and empty `tags`, `links`, `attributes`, `preconditionSteps`, `postconditionSteps`
- `replace_test_case_steps_with_shared_step`: required `testCaseId`, `sharedStepId`; plus exactly one of `stepIds` or `stepIndexes`; optional `parameterValues`
- `extract_shared_step_from_test_case_steps`: required `testCaseId`, `projectId`, `sectionId`, `name`, `state`, `priority`; plus exactly one of `stepIds` or `stepIndexes`; optional `parameterValues`, `entityTypeName`

Shared step tools use Test IT work item endpoints upstream. Shared-step references are represented in Test IT steps by `workItemId`. Replacement tools fetch the current test case, update only its step list, and send the sanitized update model back through `PUT /api/v2/workItems`.

## Test Runs

- `list_test_runs`: required `projectId`; optional `page`, `pageSize`, `testPlanId`, `notStarted`, `inProgress`, `stopped`, `completed`, `createdDateFrom`, `createdDateTo`, `OrderBy`, `SearchField`, `SearchValue`
- `get_test_run`: required `testRunId`
- `create_test_run`: required `projectId`, `name`; additional Test IT fields are passed through
- `update_test_run`: required `testRunId`; additional Test IT fields are passed through
- `complete_test_run`: required `testRunId`

If state flags are omitted, `list_test_runs` sends all four state flags as true.

## Test Results

- `list_test_results`: required `projectId`; optional `testRunId`, `testCaseId`, `page`, `pageSize`, `OrderBy`, `SearchField`, `SearchValue`
- `get_test_result`: required `testResultId`
- `create_test_result`: required `projectId`; additional Test IT fields are passed through
- `update_test_result`: required `testResultId`; additional Test IT fields are passed through

`list_test_results` uses `POST /api/v2/testResults/search`. The service sends `projectIds` and maps `testCaseId` to upstream `workItemIds`.

## Links

- `link_test_cases_to_suite_or_plan`: required `parentType`, `parentId`, `testCaseIds`
- `unlink_test_cases_from_suite_or_plan`: required `parentType`, `parentId`, `testCaseIds`

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
