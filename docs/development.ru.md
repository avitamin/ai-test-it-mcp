# Заметки по разработке

[English](development.md) | [Русский](development.ru.md)

## Структура проекта

- `main.py`: минимальный local entrypoint
- `mcp_server/server.py`: регистрация MCP tools и bootstrap сервера
- `mcp_server/mcp_protocol.py`: `stdio` transport и JSON-RPC handling
- `mcp_server/testit_client.py`: HTTP-клиент Test IT
- `mcp_server/services.py`: tool-level use cases и validation аргументов
- `mcp_server/config.py`: parsing конфигурации окружения
- `mcp_server/models.py`: shared response и pagination models
- `mcp_server/errors.py`: error categories и HTTP status mapping
- `tests/`: offline unit tests
- `http_client/`: JetBrains HTTP Client smoke checks для предположений об upstream Test IT API

## Тестирование

Запустите полный unit test suite:

```bash
python3 -m unittest discover -s tests -v
```

Текущее test coverage включает:

- config parsing
- error mapping
- базовые проверки MCP protocol
- service-layer validation и request shaping

Tests используют стандартную библиотеку `unittest`. Держите tests offline с небольшими fake clients или mocks.

## Smoke Checks

Используйте JetBrains HTTP Client files в [http_client/](../http_client/) для проверки предположений об upstream Test IT API:

- [http_client/testit-smoke.http](../http_client/testit-smoke.http)
- [http_client/http-client.env.json](../http_client/http-client.env.json)
- `http_client/http-client.private.env.json` для local secrets

Рекомендуемая минимальная последовательность:

1. `List projects`
2. `List test plans`
3. `List test suites` после того, как есть реальный `testPlanId`
4. `List test runs`
5. `List test results`

Эти smoke checks проверяют Test IT endpoints напрямую, а не MCP `stdio` protocol. JetBrains HTTP Client говорит по HTTP, тогда как этот MCP server сейчас использует `stdio` JSON-RPC.

## API Shape Notes

Этот сервер не зеркалирует все Test IT endpoints вслепую.

MCP surface нормализован для LLM/tool callers, но некоторые upstream API constraints все еще важны:

- `list_test_suites` требует `testPlanId`
- `list_test_runs` scoped по project и ожидает state flags
- `list_test_results` search-based, а не простой collection `GET`
- некоторые list endpoints в Test IT возвращают arrays напрямую, а не paginated envelopes

Если вы меняете API routing assumptions, сначала проверьте их по live Swagger. Наиболее вероятные поломки связаны с endpoint shape differences между Test IT deployments.

## Ограничения

- нет support для attachments в v1
- нет MCP `resources` или `prompts`
- нет bulk operations, кроме уже exposed операций link/unlink style
- некоторые create/update payloads передаются through с минимальной normalization, поэтому callers должны держаться близко к реальным Test IT field names там, где это требуется
- реализация намеренно легковесная и использует HTTP stack стандартной библиотеки Python вместо `httpx`
