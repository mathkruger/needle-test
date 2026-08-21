# needle-test

Personal test project for experimenting with [cactus-needle](https://huggingface.co/Cactus-Compute/needle2) -- a local-first AI agent framework that runs a 14MB tool-calling LLM entirely on-device via `ctypes`. No API keys, no cloud.

## Setup

```bash
python3 -m venv .needle-test-venv
source .needle-test-venv/bin/activate
./install.sh
```

On first run the needle engine is auto-downloaded from HuggingFace (~14MB).

## Usage

```bash
./start.sh
# or
python3 src/main.py
```

Type natural language queries and the agent will decide which tools to call. Type `exit` to quit.

## Web UI & API

The agent can also be used from the browser through a built-in HTTP server (Python stdlib only, no extra dependencies):

```bash
./start.sh --web
# or
python3 src/main.py --web --host 127.0.0.1 --port 8000
```

Then open http://127.0.0.1:8000 for a minimal chat UI backed by the same local agent.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Chat web UI (single HTML file) |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/tools` | List registered tools with descriptions and parameters |
| `POST` | `/api/run` | Run a query through the agent |
| `POST` | `/api/reset` | Reset the conversation state |

### Example

```bash
curl -s http://127.0.0.1:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"query": "ping 3 times"}'
```

```json
{
  "type": "stop",
  "reasoning": "...",
  "results": [{"result": "pong pong pong", "__labels__": {"result": "Response"}}],
  "prefill_tps": 1234.5,
  "decode_tps": 89.2,
  "peak_ram_mb": 45.1,
  "confidence": 0.98
}
```

Optional body fields for `/api/run`: `max_steps` (integer, 1-32, default `8`).

> Note: the native LLM engine is a global singleton and not thread-safe, so requests are serialized with a lock - one query runs at a time.

## Tools

| Tool | Description |
|------|-------------|
| `ping` | Returns "pong" N times |
| `get_system_usage` | CPU and RAM usage (Linux, reads `/proc`) |
| `get_time_tool` | Current date and time |
| `set_volume` | Set audio volume (0-100) via PulseAudio |
| `list_tools` | Introspects registered tools at runtime |

## Adding a tool

1. Create a file in `src/tools/` with a `@needle.tool` decorated function
2. Import and register it in `src/agent.py`

See `src/tools/ping_tool.py` for the simplest example, and `AGENTS.md` for full details.
