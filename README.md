# Wedding Planner Multi-Agent System

A modular Python project that coordinates destination wedding planning through specialized AI agents.

The system uses a coordinator agent to collect user requirements, update shared state, and delegate tasks to specialist agents for:
- flight discovery (via MCP travel tools)
- venue research (via Tavily web search)
- playlist curation (via SQLite music database)

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Environment Variables](#environment-variables)
- [Installation](#installation)
- [Run the Project](#run-the-project)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Development Notes](#development-notes)

## Overview

This project demonstrates a practical multi-agent orchestration pattern using LangChain and LangGraph-style stateful agent workflows.

Key characteristics:
- clear separation of concerns between entrypoint, workflow orchestration, agent factories, and tools
- reusable tool layer for web search and database querying
- robust MCP tool-call retry interceptor for transient failures
- strongly scoped prompts per specialist agent

## Architecture

The runtime is split into focused modules:

1. Entrypoint
- `main.py` starts the async application and prints the final result.

2. Workflow orchestration
- `workflow.py` builds the coordinator agent and runs the end-to-end planning flow.

3. Agent construction
- `agent_factory.py` loads MCP travel tools and creates specialist agents.

4. Coordinator tools
- `coordinator_tools.py` defines coordinator-facing tools:
  - `update_state`
  - `search_flights`
  - `search_venues`
  - `suggest_playlist`

5. Shared infrastructure
- `tools.py` contains reusable external tools (`web_search`, `query_playlist_db`).
- `common.py` contains MCP retry interceptor logic.
- `llm.py` centralizes OpenRouter model client creation.
- `prompts.py` stores all system prompts.
- `states.py` defines the shared state schema.
- `config.py` centralizes runtime configuration constants and environment variable loading.

## Project Structure

```text
wedding_planner/
  agent_factory.py
  common.py
  config.py
  coordinator_tools.py
  llm.py
  main.py
  prompts.py
  requirements.txt
  resources/
    Chinook.db
  states.py
  tools.py
  workflow.py
```

## Requirements

- Python 3.10+
- OpenRouter API key
- Tavily API key
- Internet connectivity for MCP and web search calls

## Environment Variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## Installation

1. Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

## Run the Project

```powershell
python main.py
```

The script sends a sample wedding request and prints:
- the full agent response payload
- the final assistant message

## How It Works

1. `main.py` calls `run_wedding_planner(...)`.
2. `workflow.py` fetches travel MCP tools and builds specialist agents.
3. Coordinator tools are created and attached to the coordinator agent.
4. The coordinator gathers required fields (`origin`, `destination`, `guest_count`, `genre`) and updates shared state.
5. Specialist agents execute domain tasks.
6. Coordinator synthesizes a final wedding plan output.

## Configuration

Runtime settings are in `config.py`:

- `MODEL_NAME`: default OpenRouter model
- `TRAVEL_MCP_URL`: MCP endpoint for travel tools
- `COORDINATOR_RECURSION_LIMIT`: agent recursion guard
- `APP_TAGS`: tracing tags passed to runtime config
- `DATABASE_URI`: SQLite connection string
- `RETRYABLE_MCP_CODES`: MCP error codes to retry

To change the default model, update `MODEL_NAME`.
To target another travel MCP endpoint, update `TRAVEL_MCP_URL`.

## Troubleshooting

1. `ModuleNotFoundError` for project dependencies
- Ensure the virtual environment is activated.
- Reinstall dependencies with `pip install -r requirements.txt`.

2. Missing API keys
- Verify `.env` contains valid `OPENROUTER_API_KEY` and `TAVILY_API_KEY`.

3. MCP travel tool failures
- Transient errors are retried automatically by `RetryMCPInterceptor`.
- Confirm network access to the configured MCP endpoint.

4. Playlist query issues
- Confirm `resources/Chinook.db` exists.
- Validate `DATABASE_URI` in `config.py`.

## Development Notes

Recommended next improvements:

1. Add automated tests for coordinator tools and workflow orchestration.
2. Add logging configuration with structured logs instead of print statements.
3. Add CLI arguments for dynamic user request input.
4. Add type-checking and linting in CI.
5. Add prompt and model configuration via environment variables for deployment flexibility.
