# HTTP Client smoke checks

[English](README.md) | [Русский](README.ru.md)

`http_client/testit-smoke.http` is a JetBrains HTTP Client collection for validating the Test IT REST API assumptions used by this MCP server.

Main project documentation lives in [README.md](../README.md).

## What it verifies

- `Authorization: Bearer <token>` works
- `/api/v2` base path works
- Core read-only endpoints respond for:
  - projects
  - test plans by project
  - test suites by test plan
  - project work items
  - project test runs
  - test results search

## How to run

1. Fill `http_client/http-client.env.json`
2. Open `http_client/testit-smoke.http` in IntelliJ IDEA or PyCharm
3. Select the `local` environment
4. Run requests one by one

## Important note

These files smoke-test the upstream Test IT REST API, not the MCP `stdio` protocol itself.

JetBrains HTTP Client speaks HTTP, while this MCP server currently uses `stdio` JSON-RPC.  
If these requests pass, the remaining MCP-specific validation should be done with a small client script or an MCP host.
