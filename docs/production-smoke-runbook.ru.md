# Runbook production MCP smoke

[English](production-smoke-runbook.md) | [Русский](production-smoke-runbook.ru.md)

Этот runbook описывает безопасное ручное проведение smoke-проверки Test IT MCP server на боевом контуре Test IT. Фокус: MCP `stdio`, metadata tools, validation аргументов и безопасность preview/apply. Он не заменяет JetBrains HTTP Client smoke checks для upstream API из [http_client/README.ru.md](../http_client/README.ru.md).

## Правила безопасности

- По возможности используйте Test IT token с минимальными правами.
- Не сохраняйте приватные production IDs в заметках, чатах, коммитах или скриншотах.
- Сначала выполняйте read-only и preview checks.
- Не запускайте `apply_delete_test_case`, `apply_complete_test_run` или `apply_unlink_test_cases_from_suite_or_plan` на реальных production-данных.
- Любой mutating `apply_*` запускайте только на disposable production test object, который создан для smoke и явно разрешен к удалению или изменению.
- Немедленно останавливайтесь при неожиданной успешной мутации, неожиданном upstream call во время preview, authentication error или bypass schema validation.

## Предусловия

- Локальный checkout содержит именно ту сборку, которую нужно проверить на production smoke.
- Environment variables заданы локально и не попадают в git:
  - `TESTIT_BASE_URL`
  - `TESTIT_TOKEN`
  - optional `TESTIT_AUTH_TYPE`, default `private_token`
- Подготовлена non-sensitive smoke record с placeholder-safe identifiers:
  - project ID для read checks
  - optional disposable test case ID
  - optional disposable test run ID
  - optional disposable suite или plan ID для link checks

## Безопасная MCP smoke sequence

Запустите локальный `stdio` сценарий. Placeholder IDs заменяйте только в terminal session:

```bash
printf '%s\n' \
'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}' \
'{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
'{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_projects","arguments":{"page":1,"pageSize":1}}}' \
'{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"preview_delete_test_case","arguments":{"testCaseId":"replace-disposable-test-case-id"}}}' \
| python3 main.py
```

Ожидаемые результаты:

- `initialize` возвращает server info и `tools` capability.
- `tools/list` содержит базовые tools и generated `preview_*` / `apply_*` tools для high-impact operations.
- У `delete_test_case` есть `risk=destructive`, `destructive=true`, `highImpact=true` и `supportsPreview=true`.
- `preview_delete_test_case` возвращает `upstream.willCallUpstream=false`, `applyTool=apply_delete_test_case`, target ID и `operationId`.
- `list_projects` возвращает normalized paginated response или mapped Test IT authentication/authorization error.

## Негативные safety checks

Используйте `operationId` из preview response, но намеренно измените target ID:

```bash
printf '%s\n' \
'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18"}}' \
'{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"apply_delete_test_case","arguments":{"testCaseId":"replace-different-test-case-id","operationId":"replace-operation-id-from-preview"}}}' \
'{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"create_test_case","arguments":{"projectId":"replace-project-id","sectionId":"replace-section-id","name":"Smoke","state":"NotReady","priority":"Medium","steps":[{"action":"Open"}],"unexpected":"must-be-rejected"}}}' \
| python3 main.py
```

Ожидаемые результаты:

- Changed arguments для `apply_delete_test_case` возвращают `ValidationError` с `field=operationId`.
- Unknown fields для `create_test_case` возвращают `ValidationError` с `details.fields=["unexpected"]`.
- Эти negative checks не удаляют и не создают объекты в Test IT.

## Optional disposable apply check

Запускайте только если disposable object явно подготовлен для production smoke:

1. Выполните preview нужной операции и сохраните возвращенный `operationId` локально.
2. Повторно прочитайте target object через read-only tool.
3. Выполните apply с теми же аргументами плюс `operationId`.
4. Повторно прочитайте или найдите target area, чтобы проверить, что изменился только disposable object.
5. Зафиксируйте только sanitized results: tool name, outcome, timestamp и требовался ли rollback или cleanup.

Предпочтительные disposable apply checks:

- `apply_update_test_case` с безвредным изменением name или description на disposable test case.
- `apply_parameterize_test_case` только если disposable parameters и test case data уже существуют.

Не выполняйте destructive apply checks на production, если disposable object не был создан специально для smoke и deletion явно не согласован.

## Pass / fail criteria

Pass, если:

- read-only tools возвращают expected normalized responses;
- tool metadata корректно маркирует destructive и high-impact tools;
- preview tools не вызывают mutating upstream endpoints;
- измененные `operationId` arguments отклоняются;
- unknown write fields отклоняются до upstream calls;
- optional disposable apply меняет только согласованный disposable object.

Fail, если:

- preview выглядит как mutation;
- для high-impact tools отсутствуют generated preview/apply tools;
- destructive metadata отсутствует или некорректна;
- strict validation принимает unknown write fields;
- `apply_*` принимает аргументы, отличающиеся от previewed arguments;
- изменен любой production object вне disposable smoke scope.

## Handoff notes

Для PR или release handoff укажите:

- Test IT contour name как non-secret label, не private URL.
- Выполненную tool sequence.
- Только sanitized IDs или aliases.
- Pass/fail result для каждой проверки.
- Подтверждение, что destructive apply не запускался на реальных production data.
