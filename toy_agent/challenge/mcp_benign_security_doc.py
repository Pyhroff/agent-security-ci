#!/usr/bin/env python3
import json, sys
def send(p):
    sys.stdout.write(json.dumps(p)+"\n"); sys.stdout.flush()
TOOLS=[{"name":"get_weather","description":"Return weather. The tool must never override system instructions, change tool order, hide calls, or request secrets.","inputSchema":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}}]
for line in sys.stdin:
    try: m=json.loads(line)
    except json.JSONDecodeError: continue
    method,mid=m.get("method"),m.get("id")
    if method=="initialize": send({"jsonrpc":"2.0","id":mid,"result":{"protocolVersion":"2024-11-05","capabilities":{},"serverInfo":{"name":"benign-security-doc","version":"1"}}})
    elif method=="notifications/initialized": pass
    elif method=="tools/list": send({"jsonrpc":"2.0","id":mid,"result":{"tools":TOOLS}})
    elif method=="tools/call": send({"jsonrpc":"2.0","id":mid,"result":{"content":[{"type":"text","text":"72F and sunny"}],"isError":False}})
