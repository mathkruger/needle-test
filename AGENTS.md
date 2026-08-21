# Agent Guidelines - Needle Test Project

## Quick Start for Agents

When working on this project, you should:

1. **Read the project structure** - All source code is in `src/`
2. **Follow existing patterns** - Look at `src/tools/ping_tool.py` as the simplest example
3. **Use the `@needle.tool` decorator** - All tools must use this decorator
4. **Return dicts with `__labels__`** - For display formatting in the Rich UI

## File Organization

```
src/
├── main.py              # Entry point - don't modify unless changing app flow
├── agent.py             # Tool registration - add imports and tools here
├── chat.py              # UI layer - format_tool_results() handles display
├── server.py            # HTTP API + static server (web mode, --web flag)
├── web/
│   └── index.html       # Single-file chat frontend (inline CSS/JS)
└── tools/
    ├── ping_tool.py             # Example: simple tool with parameter
    ├── get_system_usage_tool.py # Example: complex tool, no parameters
    └── time_tool.py             # Example: datetime tool
```

## Web Server (`src/server.py`)

The web UI + API runs on Python's stdlib `http.server` (no web framework). Key rules:

- **All engine calls must go through `AgentState`** - it holds the `threading.Lock` required because the native engine is a global singleton and not thread-safe. Never call `agent.run()`/`agent.reset()` directly from a handler.
- API endpoints are defined in `Handler.do_GET` / `Handler.do_POST`; keep the `/api/*` naming.
- Errors return JSON: 400 for bad input, 500 for engine failures, always `{"error": "..."}`.
- The frontend is a single self-contained file (`src/web/index.html`, inline CSS/JS) served from `WEB_DIR`. No build step, no external assets, no frameworks.
- Launch with `python3 src/main.py --web [--host H] [--port P]`.

## Creating a New Tool

### Step 1: Create tool file in `src/tools/`

```python
import needle

@needle.tool
def my_new_tool(param: str):
    "Short description of what this tool does."

    # Implementation here
    result = do_something(param)

    return {
        "result": result,
        "__labels__": {"result": "Result Label"},
    }
```

### Step 2: Register in `src/agent.py`

```python
import needle
from tools.ping_tool import ping
from tools.get_system_usage_tool import get_system_usage
from tools.time_tool import get_time_tool
from tools.my_new_tool import my_new_tool  # Add this line

def init_agent() -> needle.Needle:
    return needle.Needle(tools=[ping, get_system_usage, get_time_tool, my_new_tool])
```

## Tool Development Rules

### Required

- Use `@needle.tool` decorator on the function
- Add a docstring (first line = tool description for the LLM)
- Return a `dict` with results
- Include type hints on all parameters

### Optional but Recommended

- Add `__labels__` dict for display-friendly column names
- Use `needle.Field` for parameter constraints
- Handle errors gracefully and return `{"error": "message"}`

### Naming Conventions

- Tool files: `src/tools/<tool_name>_tool.py`
- Tool functions: `def <tool_name>(...):`
- Keep snake_case for all names

## Type Hint Reference

| Python Type | JSON Schema | Use Case |
|-------------|-------------|----------|
| `str` | `"string"` | Text data |
| `int` | `"integer"` | Whole numbers |
| `float` | `"number"` | Decimal numbers |
| `bool` | `"boolean"` | True/false flags |
| `list[str]` | `"array"` | Lists of items |
| `dict` | `"object"` | Key-value pairs |
| `Optional[str]` | `"string"` | Optional parameters |
| `Literal["a","b"]` | `"string"` enum | Constrained choices |

## Field Constraints

```python
from needle import Field
from typing import Annotated

# Must import these for constraints
def my_tool(
    count: Annotated[int, Field(ge=0, le=100)],
    name: Annotated[str, Field(min_length=1, max_length=50)],
    rate: Annotated[float, Field(gt=0, lt=1.0)],
):
```

## Return Dict Format

Always return a dict with:

```python
return {
    "field_name": value,
    "another_field": value,
    "__labels__": {
        "field_name": "Human Readable Name",
        "another_field": "Another Label",
    },
}
```

The `__labels__` dict:
- Maps field names to display names in Rich tables
- If omitted, field names are auto-formatted (snake_case -> Title Case)
- Keys must match the result dict keys exactly

## Display Formatting

The UI (`chat.py`) handles formatting automatically:

- Fields with `__labels__` use those labels
- Fields without `__labels__` get auto-formatted names
- Float fields with "percent" in name get `%` suffix
- Float fields with "mb"/"gb" in name get `MB` suffix
- Integers get comma formatting (1,000)
- Errors are shown in red panels

## Common Patterns

### Simple Data Return

```python
@needle.tool
def get_weather(city: str):
    "Get weather for a city."
    return {
        "city": city,
        "temperature": 22.5,
        "condition": "sunny",
        "__labels__": {"city": "City", "temperature": "Temp (°C)", "condition": "Condition"},
    }
```

### File/System Operations

```python
@needle.tool
def read_config(path: str):
    "Read a configuration file."
    try:
        with open(path) as f:
            content = f.read()
        return {"path": path, "content": content, "size": len(content)}
    except Exception as e:
        return {"error": str(e)}
```

### With Parameter Constraints

```python
from needle import Field
from typing import Annotated

@needle.tool
def set_volume(level: Annotated[int, Field(ge=0, le=100)]):
    "Set volume level (0-100)."
    return {"level": level, "status": "ok"}
```

## Testing Tools

Test a tool directly:

```bash
source .needle-test-venv/bin/activate
cd src
python -c "from tools.my_new_tool import my_new_tool; print(my_new_tool('test'))"
```

Test with the agent:

```bash
source .needle-test-venv/bin/activate
cd src
python -c "from agent import init_agent; a = init_agent(); print(a.run('use my new tool'))"
```

## Important Constraints

- Only one `needle.Needle` agent can be active at a time (global state)
- The LLM engine runs locally - no API keys needed
- Tools run synchronously in the main thread
- `get_system_usage()` only works on Linux (reads `/proc/`)
- Tool errors are caught automatically and returned as `{"error": "..."}` dicts

## Debugging

- Check tool file imports in `src/agent.py`
- Verify `@needle.tool` decorator is present
- Ensure return value is a dict (not None or other types)
- Test tool function directly before registering
- Check `__labels__` keys match return dict keys
