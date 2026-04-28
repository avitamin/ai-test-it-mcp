# MCP Tool Catalog

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

- `search_test_cases`: required `projectId`; optional `page`, `pageSize`, `search`, `updatedFrom`, `updatedTo`, `includeDeleted`
- `get_test_case`: required `testCaseId`
- `create_test_case`: required `projectId`, `name`; additional Test IT fields are passed through
- `update_test_case`: required `testCaseId`; additional Test IT fields are passed through
- `delete_test_case`: required `testCaseId`

Test cases use Test IT work item endpoints upstream.

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
