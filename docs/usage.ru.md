# Usage и конфигурация

[English](usage.md) | [Русский](usage.ru.md)

## Требования

- Python `3.12+`
- доступ к Test IT instance
- валидный API token

Пакет не имеет внешних runtime-зависимостей.

## Конфигурация

Сервер читает конфигурацию из environment variables.

Обязательные:

- `TESTIT_BASE_URL`
- `TESTIT_TOKEN`

Опциональные:

- `TESTIT_AUTH_TYPE`, default `private_token`; supported values: `private_token` и `bearer`
- `TESTIT_TIMEOUT_SECONDS`, default `30`
- `TESTIT_VERIFY_SSL`, default `true`
- `LOG_LEVEL`, default `INFO`

Пример:

```bash
export TESTIT_BASE_URL="https://testit.example.com"
export TESTIT_TOKEN="your-token"
export TESTIT_AUTH_TYPE="private_token"
export TESTIT_TIMEOUT_SECONDS="30"
export TESTIT_VERIFY_SSL="true"
export LOG_LEVEL="INFO"
```

`TESTIT_TOKEN` должен содержать только raw token value. Сервер сам добавляет authorization prefix. По умолчанию отправляется `Authorization: PrivateToken <token>` для приватных API-токенов Test IT, документированных как `PrivateToken {API Secret Key}`. Используйте `TESTIT_AUTH_TYPE=bearer`, чтобы отправлять `Authorization: Bearer <token>`, только если нужен Bearer token.

Boolean values, такие как `TESTIT_VERIFY_SSL`, принимают `1`, `true`, `yes` и `on` как true, либо `0`, `false`, `no` и `off` как false.

## Запуск

Запустите сервер напрямую:

```bash
python3 main.py
```

Или через console entrypoint, объявленный в `pyproject.toml`, после установки пакета:

```bash
mcp-server
```

Для editable install используйте virtual environment и выполните:

```bash
python3 -m pip install -e .
```

Процесс остается подключенным к `stdin/stdout` и ждет MCP messages.

## MCP Protocol

Сервер поддерживает:

- `initialize`
- `tools/list`
- `tools/call`

Transport: `stdio` with newline-delimited JSON-RPC messages.

Успешные tool responses включают:

- `content`
- `structuredContent`
- `isError: false`

Ошибки возвращаются как JSON-RPC errors с normalized error codes в `error.data.code`.

## Примеры

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

`list_test_suites` требует `testPlanId`, а не `projectId`.

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

### List Test Runs

```json
{
  "jsonrpc": "2.0",
  "id": 8,
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
  "id": 9,
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
