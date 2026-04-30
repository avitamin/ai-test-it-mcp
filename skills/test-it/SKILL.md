---
name: test-it
description: Use a Test IT MCP server for Test IT REST API work. Use when an agent needs to read, search, create, update, delete, link, or inspect Test IT projects, test plans, test suites, test cases, test runs, or test results through an `ai_test_it` MCP server.
---

# Test IT

## Requirements

Use this skill when an `ai_test_it` MCP server is available. The server should expose Test IT tools such as `list_projects`, `list_test_plans`, `search_test_cases`, `list_test_runs`, and related create/update/link tools.

Typical MCP server configuration needs:

- `TESTIT_BASE_URL`: Test IT base URL.
- `TESTIT_TOKEN`: raw token value. Do not print, store, or infer this value.
- `TESTIT_AUTH_TYPE`: optional; use the server default unless the user or local setup says otherwise.
- `TESTIT_TIMEOUT_SECONDS`, `TESTIT_VERIFY_SSL`, `LOG_LEVEL`: optional runtime settings.

Never ask the user to paste secrets into chat unless there is no safer setup path. If the MCP server is unavailable or misconfigured, explain the missing capability and ask the user to configure the MCP server instead of trying to call the Test IT REST API directly.

## Workflow

Use the `ai_test_it` MCP server for live Test IT operations instead of calling the REST API directly.

1. Confirm the needed entity and identifier scope before write operations. Prefer read-first steps such as `list_projects`, `get_project`, `list_test_plans`, `search_test_cases`, or `list_test_runs`.
2. Use the MCP tools with explicit IDs from prior results. Do not invent Test IT UUIDs, project IDs, private endpoints, or tokens.
3. Keep pagination bounded. Start with `pageSize` 20 unless the user asks for a wider result set; never exceed `pageSize` 100.
4. For create, update, delete, complete, link, and unlink operations, state the intended change before using the tool when the prompt is ambiguous or the operation is destructive.
5. Summarize results in user terms. Include entity names, IDs, statuses, and next steps that matter; do not expose credentials or raw private configuration values.

## Project Resolution

Resolve the Test IT project before project-scoped MCP calls. Do not guess the project from a fuzzy name match, a likely default, or the first similar `list_projects` result.

Use this order:

1. Use an explicit `projectId` or exact project name from the current user request.
2. If the request does not identify a project, look for project context in local agent instructions, such as `AGENTS.md`, `CLAUDE.md`, `.agents/`, or a separate instruction file explicitly named by the user.
3. If no project context is available, ask the user which Test IT project to use before making live MCP calls.
4. If multiple candidate projects match a provided name, ask the user to choose one before continuing.

Use `list_projects` only when the user asks to find or show projects, or when an exact project name must be resolved to an ID. For write operations, proceed only after the project and target entity or parent ID are explicit in the request, local instructions, or a confirmed read result.

## MCP Usage Examples

Use these examples as common MCP call patterns. They are written for an agent that can call the `ai_test_it` MCP tools directly; do not wrap them in raw JSON-RPC unless the user explicitly asks for protocol-level examples.

### List Test Plans For A Project

User asks: "Show test plans for project X."

Required context: explicit `projectId` or exact project name. If only a name is provided, resolve it to a single project ID before listing plans.

MCP call:

```json
{
  "tool": "list_test_plans",
  "arguments": {
    "projectId": "replace-project-id"
  }
}
```

Response guidance: return the plan names, IDs, and any status or deleted marker present in the result. If there are more pages, mention that more results are available.

### Search Test Cases

User asks: "Find test cases containing Y in project X."

Required context: project plus optional search text. If project context is missing, ask which project to use before calling MCP.

MCP call:

```json
{
  "tool": "search_test_cases",
  "arguments": {
    "projectId": "replace-project-id",
    "search": "replace-search-text",
    "page": 1,
    "pageSize": 20
  }
}
```

Response guidance: summarize matching test case names and IDs. If no results are found, say that clearly and offer to broaden the search only when useful.

### List Test Suites For A Test Plan

User asks: "Show suites in test plan Z."

Required context: `testPlanId`. Do not call `list_test_suites` with only `projectId`.

MCP call:

```json
{
  "tool": "list_test_suites",
  "arguments": {
    "testPlanId": "replace-test-plan-id"
  }
}
```

Response guidance: return suite names and IDs. If the user gave a plan name instead of an ID, first resolve or ask for the exact plan.

### List Test Runs

User asks: "Show recent runs for project X."

Required context: project. Optional filters include `testPlanId`, state flags, date range, and search fields.

MCP call:

```json
{
  "tool": "list_test_runs",
  "arguments": {
    "projectId": "replace-project-id",
    "page": 1,
    "pageSize": 20
  }
}
```

Response guidance: summarize run names, IDs, states, and dates when present. If state flags are omitted, the server includes not started, in progress, stopped, and completed runs.

### List Test Results

User asks: "Show results for run R in project X" or "Show results for test case C."

Required context: project plus optional `testRunId` or `testCaseId`.

MCP call:

```json
{
  "tool": "list_test_results",
  "arguments": {
    "projectId": "replace-project-id",
    "testRunId": "replace-test-run-id",
    "page": 1,
    "pageSize": 20
  }
}
```

Response guidance: summarize result IDs, linked test case or run IDs, outcome/status fields, and any failure detail available in the result. Omit `testRunId` or use `testCaseId` when the user asks for a different result scope.

### Link Test Cases To A Suite Or Plan

User asks: "Add these test cases to suite S" or "Link cases to plan P."

Required context: confirmed `parentType`, `parentId`, and non-empty `testCaseIds`. Confirm the intended link operation before calling MCP if the user did not provide exact IDs.

MCP call:

```json
{
  "tool": "link_test_cases_to_suite_or_plan",
  "arguments": {
    "parentType": "test_suite",
    "parentId": "replace-suite-or-plan-id",
    "testCaseIds": [
      "replace-test-case-id"
    ]
  }
}
```

Response guidance: state what was linked and include the parent ID and test case IDs. Use `parentType: "test_plan"` only when linking directly to a test plan.

### Extract Shared Step From Test Case Steps

User asks: "Сделай из X Y Z шагов общий шаг в тест-кейсе A."

Required context: confirmed `projectId`, `sectionId`, `testCaseId`, new shared step name, `state`, `priority`, and either upstream step IDs or exact 1-based step indexes from `get_test_case_steps`. Read the test case first when the user describes steps by text.

MCP call:

```json
{
  "tool": "extract_shared_step_from_test_case_steps",
  "arguments": {
    "projectId": "replace-project-id",
    "sectionId": "replace-section-id",
    "testCaseId": "replace-test-case-id",
    "name": "replace-shared-step-name",
    "state": "NotReady",
    "priority": "Medium",
    "stepIndexes": [1, 2, 3]
  }
}
```

Response guidance: state the created shared step ID and which source step indexes were replaced. If step text is ambiguous, ask the user to confirm the exact steps before writing.

### Replace Test Case Steps With Existing Shared Step

User asks: "Замени шаги X, Y на общий шаг Z в тест-кейсе B."

Required context: confirmed `testCaseId`, `sharedStepId`, and selected steps by `stepIds` or 1-based `stepIndexes`. Use `search_shared_steps` when the user gives a shared step name instead of an ID.

MCP call:

```json
{
  "tool": "replace_test_case_steps_with_shared_step",
  "arguments": {
    "testCaseId": "replace-test-case-id",
    "sharedStepId": "replace-shared-step-id",
    "stepIndexes": [2, 3]
  }
}
```

Response guidance: state the shared step ID and replaced step indexes. Test IT stores the shared-step link in the step `workItemId`; if read-back shows an empty plain step without `workItemId`, stop and report a contract problem.

### Parameterize A Test Case

User asks: "Добавь параметризацию в тест-кейс."

Required context: confirmed `testCaseId`, parameter names and defaults/values, and optional literal replacements in steps. First call `get_test_case_steps` when parameters need to be found, created, or clarified from existing step text. This tool updates step text placeholders; Test IT parameter-set persistence through iterations is not expanded yet.

MCP call:

```json
{
  "tool": "parameterize_test_case",
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
```

Response guidance: summarize changed parameter names and whether step text was updated. If a parameter already exists with a different definition, resolve the conflict with the user before setting `allowParameterOverwrite`.

### Draft Test Case From Code

User asks: "По коду из файла составь тест-кейс."

Workflow: read the requested local file with normal code-reading tools, identify externally observable behavior, derive concise test steps and expected results, then create the Test IT case with `create_test_case`. Do not ask the Test IT MCP server to read arbitrary files.

Response guidance: include the new test case ID and a short summary of covered behavior.

### Draft Automated Test From Test Case And Inputs

User asks: "По тест-кейсу и страничке/локаторам/cURL напиши тест."

Workflow: read the Test IT case with `get_test_case`, inspect the user-provided page context, locators, or cURL using normal project tools, then edit the target test file outside this MCP server. Use Test IT tools only to read or update Test IT entities.

Response guidance: identify the generated or edited test file, framework assumptions, and any locator or API gaps that still need user confirmation.

## Tool Catalog

Common entry points:

- Projects: `list_projects`, `get_project`
- Test plans: `list_test_plans`, `get_test_plan`, `create_test_plan`, `update_test_plan`
- Test suites: `list_test_suites`, `get_test_suite`, `create_test_suite`, `update_test_suite`
- Test cases: `search_test_cases`, `get_test_case`, `create_test_case`, `update_test_case`, `delete_test_case`
- Test case steps and shared steps: `get_test_case_steps`, `search_shared_steps`, `create_shared_step`, `replace_test_case_steps_with_shared_step`, `extract_shared_step_from_test_case_steps`, `parameterize_test_case`
- Test runs: `list_test_runs`, `get_test_run`, `create_test_run`, `update_test_run`, `complete_test_run`
- Test results: `list_test_results`, `get_test_result`, `create_test_result`, `update_test_result`
- Links: `link_test_cases_to_suite_or_plan`, `unlink_test_cases_from_suite_or_plan`

Important constraints:

- `list_test_suites` requires `testPlanId`, not `projectId`.
- Link `parentType` must be `test_suite` or `test_plan`.
- `list_test_results` maps `testCaseId` to upstream work item IDs in the Test IT server implementation used by this skill.
- If `list_test_runs` state flags are omitted, the server should include not started, in progress, stopped, and completed runs.

## Optional Repository Context

If this skill is installed from the `ai-test-it-mcp` repository, use `docs/mcp-tools.md` for the full tool catalog, `docs/codex-mcp-setup.md` for local MCP setup, and `docs/usage.md` for protocol-level examples. Treat those documents as optional deeper context; the common workflow and examples above are self-contained.
