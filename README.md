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
