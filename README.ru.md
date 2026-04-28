# mcp-server

[English](README.md) | [Русский](README.ru.md)

MCP-сервер для Test IT REST API.

Сервер использует JSON-RPC через `stdio` и предоставляет task-oriented MCP tools для работы с проектами, тест-планами, тестовыми наборами, тест-кейсами, тест-ранами и тестовыми результатами.

## Статус

Проект реализован как легковесный сервер на Python 3.12 без внешних runtime-зависимостей.

Текущая реализация выровнена с Test IT Swagger contract. Для проверки предположений об endpoint'ах используйте Swagger UI и OpenAPI source, доступные в вашем Test IT instance.

Важные API-specific решения уже отражены в коде:

- auth header: `Authorization: Bearer <token>`
- тестовые наборы запрашиваются по тест-плану, а не по проекту
- тест-планы запрашиваются по проекту
- тест-раны запрашиваются по проекту с явными state flags
- тестовые результаты ищутся через `POST /api/v2/testResults/search`

## Быстрый старт

Требования:

- Python `3.12+`
- доступ к Test IT instance
- валидный API token

Настройте окружение:

```bash
export TESTIT_BASE_URL="https://testit.example.com"
export TESTIT_TOKEN="your-token"
```

`TESTIT_TOKEN` должен содержать только raw token value. Сервер сам добавляет префикс `Bearer`.

Запустите сервер напрямую:

```bash
python3 main.py
```

Или через console entrypoint, объявленный в `pyproject.toml`:

```bash
mcp-server
```

Процесс остается подключенным к `stdin/stdout` и ждет MCP messages.

## Документация

- [Индекс документации](docs/README.ru.md)
- [Usage и конфигурация](docs/usage.ru.md)
- [Каталог MCP tools](docs/mcp-tools.ru.md)
- [Заметки по разработке](docs/development.ru.md)
- [HTTP Client smoke checks](http_client/README.ru.md)

## Структура проекта

- [main.py](main.py): минимальный entrypoint
- [mcp_server/server.py](mcp_server/server.py): регистрация MCP tools и bootstrap сервера
- [mcp_server/mcp_protocol.py](mcp_server/mcp_protocol.py): `stdio` transport и JSON-RPC handling
- [mcp_server/testit_client.py](mcp_server/testit_client.py): HTTP-клиент Test IT
- [mcp_server/services.py](mcp_server/services.py): tool-level use cases и validation аргументов
- [tests/](tests): unit tests
- [http_client/testit-smoke.http](http_client/testit-smoke.http): JetBrains HTTP Client smoke checks для предположений об upstream Test IT API

## Тестирование

Запустите unit test suite:

```bash
python3 -m unittest discover -s tests -v
```
