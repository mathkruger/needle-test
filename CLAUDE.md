# Needle Test - AI Agent Project

## Overview

A Python CLI chatbot powered by `cactus-needle`, a local-first AI agent framework that runs a native LLM engine via ctypes. The agent can use tools to answer user queries.

## Tech Stack

- Python 3.12
- `cactus-needle` (imported as `needle`) - Local LLM agent framework
- `rich` - Terminal UI formatting
- Python stdlib `http.server` - Web UI + API server (no web framework)

## Project Structure

```
src/
  main.py          - Entry point: creates agent, starts chat REPL or web server (--web)
  agent.py         - Agent factory: registers tools with needle
  chat.py          - Rich-powered interactive chat loop
  server.py        - HTTP API + static file server for the web UI
  web/
    index.html     - Single-file chat frontend (inline CSS/JS, no frameworks)
  tools/
    ping_tool.py             - Returns pong (simple test tool)
    get_system_usage_tool.py - CPU and RAM stats from /proc
    time_tool.py             - Current date/time info
```

## How to Run

```bash
source .needle-test-venv/bin/activate
python3 src/main.py            # terminal chat REPL
python3 src/main.py --web      # web UI + API on http://127.0.0.1:8000
# or
./start.sh                     # passes args through: ./start.sh --web --port 8000
```

### CLI flags

| Flag | Default | Description |
|------|---------|-------------|
| `--web` | off | Start the web UI + API server instead of the REPL |
| `--host` | `127.0.0.1` | Web server bind address |
| `--port` | `8000` | Web server port |

## How It Works

1. `main.py` calls `init_agent()` from `agent.py` which creates a `needle.Needle` instance with registered tools
2. Terminal mode: `init_chat(agent)` starts a REPL loop that reads user input
3. Web mode (`--web`): `server.serve(agent, host, port)` starts a stdlib `ThreadingHTTPServer`
4. `agent.run(prompt)` sends the query to the local LLM which decides which tools to call
5. The LLM returns `function_calls` which are executed, results fed back, repeated up to 8 steps
6. Results are formatted as Rich tables with labels (terminal) or HTML cards (web)

## HTTP API

Defined in `src/server.py`. All engine access goes through `AgentState`, which wraps every call in a `threading.Lock` because the native engine is a global singleton and not thread-safe - requests are serialized.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serves `src/web/index.html` |
| `GET` | `/api/health` | `{"status": "ok", "model": "needle-2"}` |
| `GET` | `/api/tools` | Tool names, descriptions, parameter names (introspected from `_needle_tool` schemas) |
| `POST` | `/api/run` | Body `{"query": str, "max_steps": int=8}`; returns the raw `agent.run()` dict as JSON |
| `POST` | `/api/reset` | Resets conversation state; returns `{"ok": true}` |

Errors: invalid JSON body or missing/empty `query` -> 400; engine failure -> 500; both return `{"error": "..."}`.

Example:

```bash
curl -s http://127.0.0.1:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"query": "ping 3 times"}'
```

## Creating New Tools

### Template

```python
import needle

@needle.tool
def my_tool_name(param1: str, param2: int):
    "Description of what the tool does."

    # Tool logic here

    return {
        "field_name": value,
        "__labels__": {"field_name": "Display Name"},
    }
```

### Registration

1. Create a new file in `src/tools/` named `my_tool_name_tool.py`
2. Import the tool function in `src/agent.py`:
   ```python
   from tools.my_tool_name_tool import my_tool_name
   ```
3. Add it to the tools list in `init_agent()`:
   ```python
   return needle.Needle(tools=[..., my_tool_name])
   ```

### Rules

- Always use `@needle.tool` decorator
- Function name becomes the tool name the LLM calls
- First line of docstring becomes the tool description
- Type hints auto-generate JSON schema (str, int, float, bool, list, dict)
- Return a dict with result fields
- Include `__labels__` dict for display-friendly column names in Rich tables
- Optional parameters: use `Optional[X]` type hint or provide a default value
- For constrained values: use `needle.Field` with `Annotated`:
  ```python
  from needle import Field
  from typing import Annotated

  def my_tool(count: Annotated[int, Field(ge=0, le=100)]):
  ```

### Supported Parameter Types

| Python Type | JSON Schema |
|-------------|-------------|
| `str` | `"string"` |
| `int` | `"integer"` |
| `float` | `"number"` |
| `bool` | `"boolean"` |
| `list[X]` | `"array"` with items |
| `dict` | `"object"` |
| `Optional[X]` | type of X (not required) |
| `Literal["a", "b"]` | `"string"` with enum |
| `Enum` subclass | `"string"` with enum values |
| Pydantic `BaseModel` | nested object schema |

### Field Constraints

```python
from needle import Field
from typing import Annotated

# Numeric constraints
Annotated[int, Field(ge=0, le=100)]        # >= 0, <= 100
Annotated[float, Field(gt=0, lt=1.0)]      # > 0, < 1.0
Annotated[int, Field(multiple_of=5)]        # must be multiple of 5

# String constraints
Annotated[str, Field(min_length=1, max_length=50)]
Annotated[str, Field(pattern=r"^[a-z]+$")]
Annotated[str, Field(format="email")]

# Array constraints
Annotated[list, Field(min_items=1, max_items=10, unique_items=True)]

# Enum/const
Annotated[str, Field(enum=["a", "b", "c"])]
Annotated[str, Field(const="fixed_value")]

# With description
Annotated[int, Field(description="Number of retries")]
```

## Existing Tools Reference

### ping(times: int)
Returns "pong" repeated N times. Simple test tool.

### get_system_usage()
No parameters. Returns CPU usage (%), RAM stats (total/used/available in MB and %), core count. Reads from `/proc/stat` and `/proc/meminfo`. Linux only.

### get_time_tool()
No parameters. Returns current date, time, weekday, year/month/day/hour/minute/second.

## Agent API

```python
agent = needle.Needle(tools=[...], system="optional system prompt")

# Run with agentic loop (up to 8 steps)
result = agent.run("user query")
# result = {"reasoning": "...", "results": [...], ...}

# Single completion
response = agent.complete("prompt", max_new_tokens=256)

# Structured extraction
data = agent.extract("text to parse", schema=MyPydanticModel)
```

## Important Notes

- The native LLM engine is loaded once globally; only one agent can be active at a time
- The web server serializes engine access with a lock - one query runs at a time, no streaming
- Custom weights can be loaded via `needle.Needle(weights="path/to/weights.cact")`
- The engine runs locally - no API keys needed
- `__labels__` in tool results are optional but improve display formatting
- Tool errors are caught and returned as `{"error": "message"}` dicts
