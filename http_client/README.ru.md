# HTTP Client smoke checks

[English](README.md) | [Русский](README.ru.md)

`http_client/testit-smoke.http` - это JetBrains HTTP Client collection для проверки предположений о Test IT REST API, которые использует этот MCP server.

Основная документация проекта находится в [README.ru.md](../README.ru.md).

## Что проверяется

- работает `Authorization: Bearer <token>`
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

1. Заполните `http_client/http-client.env.json`
2. Откройте `http_client/testit-smoke.http` в IntelliJ IDEA или PyCharm
3. Выберите environment `local`
4. Запускайте requests по одному

## Важное замечание

Эти файлы smoke-test upstream Test IT REST API, а не сам MCP `stdio` protocol.

JetBrains HTTP Client говорит по HTTP, тогда как этот MCP server сейчас использует `stdio` JSON-RPC.  
Если эти requests проходят, оставшуюся MCP-specific validation нужно делать небольшим client script или MCP host.
