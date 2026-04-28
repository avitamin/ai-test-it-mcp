# mcp-server

[English](README.md) | [Русский](README.ru.md)

MCP-сервер для Test IT REST API. Он работает через JSON-RPC по `stdio` и предоставляет MCP tools для проектов, тест-планов, тестовых наборов, тест-кейсов, тест-ранов, тестовых результатов и связей между тест-кейсами и наборами или планами.

Проект реализован как легковесный сервер на Python 3.12 без внешних runtime-зависимостей.

## Требования

- Python `3.12+`
- доступ к Test IT instance
- валидный Test IT API token

## Быстрый старт

Настройте обязательное окружение:

```bash
export TESTIT_BASE_URL="https://testit.example.com"
export TESTIT_TOKEN="your-token"
```

`TESTIT_TOKEN` должен содержать только raw token value. Сервер сам добавляет префикс `Bearer`.

Запустите сервер напрямую:

```bash
python3 main.py
```

Или установите пакет в editable mode и используйте console entrypoint:

```bash
python3 -m pip install -e .
mcp-server
```

Процесс остается подключенным к `stdin/stdout` и ждет MCP messages.

## Что можно делать

Набор tools покрывает основные Test IT workflows:

- получать списки проектов и отдельные проекты
- получать, создавать, обновлять и читать тест-планы и тестовые наборы
- искать, создавать, обновлять, читать и удалять тест-кейсы
- получать, создавать, обновлять, читать и завершать тест-раны
- получать, создавать, обновлять и читать тестовые результаты
- связывать или отвязывать тест-кейсы от тестового набора или тест-плана

См. [каталог MCP tools](docs/mcp-tools.ru.md) для required arguments, pagination, response shape и error behavior.

## Заметки по API

Реализация следует предположениям, проверенным по Test IT Swagger contract. Для проверки endpoint behavior используйте Swagger UI и OpenAPI source, доступные в вашем Test IT instance.

Важное поведение:

- тестовые наборы запрашиваются по тест-плану, а не по проекту
- тест-планы и тест-раны запрашиваются по проекту
- тестовые результаты ищутся через `POST /api/v2/testResults/search`

## Куда идти дальше

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
- [http_client/testit-smoke.http](http_client/testit-smoke.http): JetBrains HTTP Client smoke checks

## Тестирование

Запустите unit test suite:

```bash
python3 -m unittest discover -s tests -v
```
