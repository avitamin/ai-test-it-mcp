# mcp-server

[English](README.md) | [Русский](README.ru.md)

MCP-сервер для Test IT REST API. Он работает через JSON-RPC по `stdio` и предоставляет MCP tools для проектов, тест-планов, тестовых наборов, тест-кейсов, тест-ранов, тестовых результатов и связей между тест-кейсами и наборами или планами.

Проект реализован как легковесный сервер на Python 3.12 без внешних runtime-зависимостей.

## Требования

- Python `3.12+`
- доступ к Test IT instance
- валидный Test IT API token

## Быстрый старт

Обычно этот server подключают к MCP client, например Codex или Claude Code. Клиент сам запускает server process и общается с ним через `stdio`.

Используйте client setup guide:

- [Быстрый старт для Codex и Claude Code](docs/mcp-client-quickstart.ru.md)

При настройке клиента понадобятся эти Test IT values:

```bash
export TESTIT_BASE_URL="https://testit.example.com"
export TESTIT_TOKEN="your-token"
# Optional: private_token или bearer; default is private_token.
export TESTIT_AUTH_TYPE="private_token"
```

`TESTIT_TOKEN` должен содержать только raw token value. Сервер сам добавляет authorization prefix. По умолчанию используются приватные API-токены Test IT, документированные как `PrivateToken {API Secret Key}`. Используйте `TESTIT_AUTH_TYPE=bearer`, только если нужен Bearer token.

## Установка Test IT Skill

Репозиторий также поставляет распространяемый skill `test-it` для агентов, которые поддерживают [skills.sh](https://skills.sh/). Skill объясняет агенту, как безопасно использовать настроенный MCP server `ai_test_it`; он не запускает и не настраивает MCP server сам.

Установите skill для Codex из этого GitHub repository:

```bash
npx skills add avitamin/ai-test-it-mcp --skill test-it --agent codex --yes
```

Для interactive default install flow, включая другие поддерживаемые agents, выполните:

```bash
npx skills add avitamin/ai-test-it-mcp --skill test-it
```

Чтобы установить skill глобально, а не в текущий project, добавьте `--global`. Чтобы проверить, что skill обнаруживается из локального checkout, выполните:

```bash
npx skills add . --skill test-it --list
```

После установки используйте prompts вроде:

```text
Use $test-it to show test plans for project <project name>.
```

Агенту всё равно нужен MCP server с именем `ai_test_it`, настроенный с `TESTIT_BASE_URL`, `TESTIT_TOKEN` и optional settings, описанными выше.

## Прямой запуск

Прямой запуск полезен для локальных проверок, разработки и protocol debugging.

Запустите server из репозитория:

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
- смотреть шаги тест-кейсов, создавать shared steps, заменять шаги тест-кейса shared step и параметризовать тест-кейсы
- получать, создавать, обновлять, читать и завершать тест-раны
- получать, создавать, обновлять и читать тестовые результаты
- связывать или отвязывать тест-кейсы от тестового набора или тест-плана

См. [каталог MCP tools](docs/mcp-tools.ru.md) для required arguments, pagination, response shape и error behavior.

## Заметки по API

Эта версия сервера ориентируется на контракт Pegasus/Test IT API v2. Для проверки формы API используйте локальный OpenAPI cache в `.local/swagger-v2.json`.

Важное поведение:

- тестовые наборы запрашиваются по тест-плану, а не по проекту
- тест-планы и тест-раны запрашиваются по проекту
- тестовые результаты ищутся через `POST /api/v2/testResults/search`

## Куда идти дальше

- [Индекс документации](docs/README.ru.md)
- [Быстрый старт для Codex и Claude Code](docs/mcp-client-quickstart.ru.md)
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
