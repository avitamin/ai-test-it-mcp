# HTTP Client smoke checks

[English](README.md) | [Русский](README.ru.md)

`http_client/testit-smoke.http` - это JetBrains HTTP Client collection для проверки предположений о Test IT REST API, которые использует этот MCP server.

Основная документация проекта находится в [README.ru.md](../README.ru.md).

Эта версия сервера ориентируется на контракт Pegasus/Test IT API v2. Используйте `.local/swagger-v2.json` как локальный OpenAPI cache при сравнении smoke checks с целевой формой API.

## Что проверяется

- работает `Authorization: PrivateToken <token>`
- работает base path `/api/v2`
- Core read-only endpoints отвечают для:
  - projects
  - test plans by project
  - test suites by test plan
  - project work items
  - shared step search and references
  - project test runs
  - test results search

## Как запускать

1. Заполните non-secret values в `http_client/http-client.env.json`
2. Поместите raw PAT token в `http_client/http-client.private.env.json`
3. Откройте `http_client/testit-smoke.http` в IntelliJ IDEA или PyCharm
4. Выберите environment `prod`
5. Запускайте requests по одному

## Важное замечание

Эти файлы smoke-test upstream Test IT REST API, а не сам MCP `stdio` protocol.

JetBrains HTTP Client говорит по HTTP, тогда как этот MCP server сейчас использует `stdio` JSON-RPC.  
Если эти requests проходят, оставшуюся MCP-specific validation нужно делать небольшим client script или MCP host.
