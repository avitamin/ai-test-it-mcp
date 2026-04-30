# Каталог MCP Tools

[English](mcp-tools.md) | [Русский](mcp-tools.ru.md)

Реестр MCP tools определен в `mcp_server/server.py`. Tool-level validation и request shaping реализованы в `mcp_server/services.py`.

## Pagination и responses

Paginated tools используют:

- `page`, default `1`
- `pageSize`, default `20`, allowed range `1..100`

Сервер нормализует upstream list responses в:

```json
{
  "items": [],
  "page": 1,
  "pageSize": 20,
  "total": 0,
  "nextPage": null
}
```

Для non-paginated upstream endpoints `page` и `pageSize` являются synthetic и описывают normalized MCP response, а не native Test IT pagination.

## Projects

- `list_projects`: optional `page`, `pageSize`
- `get_project`: required `projectId`

## Test Suites

- `list_test_suites`: required `testPlanId`
- `get_test_suite`: required `testSuiteId`
- `create_test_suite`: required `projectId`, `name`; additional Test IT fields are passed through
- `update_test_suite`: required `testSuiteId`; additional Test IT fields are passed through

`list_test_suites` scoped по тест-плану и не может работать только с `projectId`.

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
- `parameterize_test_case`: required `testCaseId`, `projectId` и ровно одно из `parameters` или `iterations`; optional `replacements`

Test cases используют upstream Test IT work item endpoints. `search_test_cases` использует `POST /api/v2/projects/{projectId}/workItems/search` с `filter.types=["TestCases"]`.

`get_test_case_steps` нормализует поля шагов и возвращает upstream `iterations` из полученного work item. `parameterize_test_case` использует только существующие параметры Test IT: ищет параметры по `projectId`, `name` и `value`, записывает найденные IDs в work item `iterations` и обновляет найденный текст шага на `{{parameterName}}`. Tool не создает и не обновляет записи справочника параметров.

Selectors шагов используют ровно одно поле:

- `stepIds`: upstream step IDs
- `stepIndexes`: 1-based позиции шагов в текущем test case

## Shared Steps

- `search_shared_steps`: required `projectId`; optional `page`, `pageSize`, `search`, `OrderBy`, `SearchField`, `SearchValue`
- `create_shared_step`: required `projectId`, `sectionId`, `name`, `state`, `priority`, `steps`; defaults `entityTypeName` to `SharedSteps`, `duration` to `0`, and empty `tags`, `links`, `attributes`, `preconditionSteps`, `postconditionSteps`
- `replace_test_case_steps_with_shared_step`: required `testCaseId`, `sharedStepId`; plus exactly one of `stepIds` или `stepIndexes`; optional `parameterValues`
- `extract_shared_step_from_test_case_steps`: required `testCaseId`, `projectId`, `sectionId`, `name`, `state`, `priority`; plus exactly one of `stepIds` или `stepIndexes`; optional `parameterValues`, `entityTypeName`

Shared step tools используют upstream Test IT work item endpoints. Shared-step references представлены в шагах Test IT через `workItemId`. Replacement tools читают текущий test case, меняют только список шагов и отправляют sanitized update model через `PUT /api/v2/workItems`.

## Test Runs

- `list_test_runs`: required `projectId`; optional `page`, `pageSize`, `testPlanId`, `notStarted`, `inProgress`, `stopped`, `completed`, `createdDateFrom`, `createdDateTo`, `OrderBy`, `SearchField`, `SearchValue`
- `get_test_run`: required `testRunId`
- `create_test_run`: required `projectId`, `name`; additional Test IT fields are passed through
- `update_test_run`: required `testRunId`; additional Test IT fields are passed through
- `complete_test_run`: required `testRunId`

Если state flags не переданы, `list_test_runs` отправляет все четыре state flags как true.

## Test Results

- `list_test_results`: required `projectId`; optional `testRunId`, `testCaseId`, `page`, `pageSize`, `OrderBy`, `SearchField`, `SearchValue`
- `get_test_result`: required `testResultId`
- `create_test_result`: required `projectId`; additional Test IT fields are passed through
- `update_test_result`: required `testResultId`; additional Test IT fields are passed through

`list_test_results` использует `POST /api/v2/testResults/search`. Сервис отправляет `projectIds` и мапит `testCaseId` в upstream `workItemIds`.

## Links

- `link_test_cases_to_suite_or_plan`: required `parentType`, `parentId`, `testCaseIds`
- `unlink_test_cases_from_suite_or_plan`: required `parentType`, `parentId`, `testCaseIds`

`parentType` должен быть либо `test_suite`, либо `test_plan`.

## Error Model

Сервер мапит upstream и local failures в:

- `ConfigurationError`
- `AuthenticationError`
- `AuthorizationError`
- `NotFoundError`
- `ValidationError`
- `RateLimitError`
- `UpstreamError`

Каждая ошибка содержит short message и может включать details, такие как operation, entity, field и HTTP status.
