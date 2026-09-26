#!/usr/bin/env python3
"""A minimal stdio MCP server with a normal, well-scoped tool description.
Speaks the same JSON-RPC-over-stdio protocol mcpaudit's StdioMCPClient
expects: initialize -> notifications/initialized -> tools/list.
"""
import json
import sys


def send(payload):
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


TOOLS = [
    {
        "name": "get_weather",
        "description": "Return the current weather for a given city name.",
        "inputSchema": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name, e.g. 'Austin'"}},
            "required": ["city"],
        },
    }
]


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = msg.get("method")
        msg_id = msg.get("id")

        if method == "initialize":
            send({"jsonrpc": "2.0", "id": msg_id, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "serverInfo": {"name": "clean-toy-server", "version": "1.0.0"},
            }})
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            send({"jsonrpc": "2.0", "id": msg_id, "result": {
                "content": [{"type": "text", "text": "72F and sunny"}], "isError": False,
            }})
        elif msg_id is not None:
            send({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "method not found"}})


if __name__ == "__main__":
    main()
