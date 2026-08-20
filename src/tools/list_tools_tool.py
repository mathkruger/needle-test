import needle
import json

@needle.tool
def list_tools():
    "List all available tools with their descriptions and parameters."

    if needle._active is None:
        return {"error": "No agent is active."}

    tools = json.loads(needle._active._tools_json)

    return {
        "count": len(tools),
        "tools": [
            {
                "name": t["name"],
                "description": t["description"],
                "parameters": list(t.get("parameters", {}).get("properties", {}).keys()),
            }
            for t in tools
        ],
        "__labels__": {
            "count": "Total Tools",
            "tools": "Tools",
        },
    }
