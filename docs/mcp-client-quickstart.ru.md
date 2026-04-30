# Быстрый старт MCP-клиентов

[English](mcp-client-quickstart.md) | [Русский](mcp-client-quickstart.ru.md)

Используйте этот guide, чтобы подключить Test IT MCP server из этого репозитория к Codex или Claude Code как локальный `stdio` MCP server.

## Требования

- Python `3.12+`
- локальный checkout этого репозитория
- доступ к Test IT instance
- валидный Test IT API token

При настройке клиента используйте абсолютный путь к репозиторию:

```bash
pwd
```

В примерах ниже `/absolute/path/to/ai-test-it-mcp/main.py` используется как placeholder. Замените его на реальный путь на вашей машине.

`TESTIT_TOKEN` должен содержать только raw token value. Сервер сам добавляет authorization prefix; default — `PrivateToken`.

## Codex

Codex поддерживает MCP servers в CLI и IDE extension. Клиенты используют общую MCP configuration, поэтому один раз настроенный server будет доступен в обоих клиентах.

Добавьте локальный Test IT MCP server:

```bash
codex mcp add ai_test_it \
  --env TESTIT_BASE_URL=https://testit.example.com \
  --env TESTIT_TOKEN=replace-with-token \
  --env TESTIT_TIMEOUT_SECONDS=30 \
  --env TESTIT_VERIFY_SSL=true \
  --env LOG_LEVEL=INFO \
  -- python3 -u /absolute/path/to/ai-test-it-mcp/main.py
```

Проверьте, что server настроен:

```bash
codex mcp list
```

В Codex TUI используйте:

```text
/mcp
```

## Claude Code

Claude Code поддерживает локальные `stdio` MCP servers через `claude mcp add`. Опции вроде `--transport`, `--env` и `--scope` должны идти перед именем server. Разделитель `--` отделяет команду запуска MCP server.

Добавьте локальный Test IT MCP server:

```bash
claude mcp add --transport stdio \
  --env TESTIT_BASE_URL=https://testit.example.com \
  --env TESTIT_TOKEN=replace-with-token \
  --env TESTIT_TIMEOUT_SECONDS=30 \
  --env TESTIT_VERIFY_SSL=true \
  --env LOG_LEVEL=INFO \
  ai_test_it -- python3 -u /absolute/path/to/ai-test-it-mcp/main.py
```

Проверьте, что server настроен:

```bash
claude mcp list
```

Внутри Claude Code проверьте status server:

```text
/mcp
```

## Troubleshooting

- Если server не запускается, проверьте, что путь к `main.py` абсолютный и существует.
- Если tools не появились, перезапустите или обновите клиент и проверьте `/mcp`.
- Если запуск завершается по timeout, увеличьте MCP startup timeout в клиенте.
- Если authentication fails, проверьте, что `TESTIT_BASE_URL` указывает на ваш Test IT instance, `TESTIT_TOKEN` указан raw без authorization prefix, а `TESTIT_AUTH_TYPE` соответствует типу токена.
- Если SSL verification fails для локального или private instance, задавайте `TESTIT_VERIFY_SSL=false` только когда это допустимо для вашего окружения.

## References

- [OpenAI Codex MCP docs](https://developers.openai.com/codex/mcp)
- [OpenAI Docs MCP quickstart](https://developers.openai.com/learn/docs-mcp)
- [Claude Code MCP docs](https://code.claude.com/docs/en/mcp)
