# Changelog

All notable changes to this project will be documented in this file.

---

## [v0.1.0] - 2025-06-11

### Added
- Initial public release of `cockroachdb-mcp-client`
- Full support for MCP-spec CRUD: `create`, `list`, `get`, `delete`, `export`
- LLM provider integration: OpenAI, Anthropic
- CLI features: `run`, `simulate`, `stream`, `model override`
- Config via `~/.config` or environment variables
- Retry support (via `tenacity`) on all HTTP operations
- Structured logging with `--log-level`
- Helpful connection error diagnostics
- CLI banner, `--version`, and completion commands

### Changed
- Refactored CLI commands for consistency and maintainability

### Known Limitations
- No `deploy` or `evaluate` command yet
- No plugin system for user-defined providers (planned)

