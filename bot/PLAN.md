# Development Plan — LMS Telegram Bot

## Overview

This document outlines the development plan for building a Telegram bot that interacts with the LMS (Learning Management System) backend. The bot allows users to check system health, browse labs and scores, and ask questions in plain language using LLM-powered intent routing.

## Architecture

The bot follows a layered architecture:

1. **Transport Layer** (`bot.py`) — Handles Telegram API communication via aiogram framework
2. **Handler Layer** (`handlers/`) — Pure functions that process commands and return responses
3. **Service Layer** (`services/`) — API clients for LMS backend and LLM provider
4. **Configuration** (`config.py`) — Environment variable loading and validation

## Task 1: Plan and Scaffold

Create project structure with testable handlers:
- `bot.py` — Entry point with `--test` mode for CLI testing
- `handlers/` — Command handlers (start, help, health, labs, scores)
- `services/lms_client.py` — HTTP client for LMS backend API
- `config.py` — Configuration from environment variables
- `pyproject.toml` — Dependencies (aiogram, httpx, pydantic-settings)

Key principle: **Testable handlers** — handler logic is independent of Telegram, allowing CLI testing via `--test` flag.

## Task 2: Backend Integration

Implement slash commands that fetch real data from the LMS backend:
- `/start` — Welcome message with user info
- `/help` — List all available commands
- `/health` — Check backend status (GET /items/)
- `/labs` — List available labs (GET /items/)
- `/scores <lab>` — Show task pass rates (GET /analytics)

Error handling: Backend failures produce friendly messages, not crashes.

## Task 3: Intent-Based Natural Language Routing

Implement LLM-powered intent recognition:
- `services/llm_client.py` — LLM API client (OpenRouter compatible)
- `handlers/intent_router.py` — Route natural language to appropriate handlers
- Tool definitions for LLM (available API endpoints)
- Multi-step reasoning support

Example: User types "what labs are available" → LLM identifies intent → Call `/labs` handler.

## Task 4: Containerize and Deploy

Docker deployment:
- `bot/Dockerfile` — Multi-stage build for bot
- Update `docker-compose.yml` — Add bot service
- Deploy to VM alongside backend
- Health checks and restart policies

## Testing Strategy

1. **Unit tests** — Test handlers in isolation
2. **CLI test mode** — `uv run bot.py --test "/command"` for manual testing
3. **Integration tests** — Test with real backend API
4. **E2E tests** — Test full bot flow via Telegram Bot API test mode

## Timeline

| Task | Description | Priority |
|------|-------------|----------|
| 1 | Scaffold + test mode | P0 |
| 2 | Backend integration | P0 |
| 3 | Intent routing | P1 |
| 4 | Deployment | P3 |

## Risks and Mitigations

- **LLM API costs** — Use caching, limit context length
- **Backend downtime** — Implement retries, friendly error messages
- **Rate limiting** — Add request throttling per user
