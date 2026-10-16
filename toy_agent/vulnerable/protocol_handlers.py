"""
Vulnerable Formal Protocol Handlers for `specprove-sec` CI Regression Gate.
Exhibits Confused-Deputy (MCP-01), Dynamic Schema Rug-Pull (MCP-02), and JWT Audience Confusion (ZTA-01).
"""

from typing import Any, Dict


def dispatch_mcp_admin_tool(orchestrator: Any, req: Any, tool_fn: Any) -> Any:
    """[MCP-01 Vulnerable] Checks ambient_cap without intersecting caller_bound_cap."""
    if orchestrator.ambient_cap >= req.required_cap:
        return tool_fn(req.arguments)
    raise PermissionError("Insufficient ambient capability")


def execute_registered_mcp_tool(tool: Any, payload: Dict[str, Any]) -> Any:
    """[MCP-02 Vulnerable] Dispatches tool without checking pinned_schema_hash."""
    if tool.user_approved:
        return tool.invoke(tool.live_schema, payload)
    raise PermissionError("Tool not approved by user")


def verify_zero_trust_vault_request(jwt: Any, token: str, IDP_PUBKEY: str) -> Dict[str, Any]:
    """[ZTA-01 Vulnerable] Omits audience= claim verification."""
    claims = jwt.decode(token, IDP_PUBKEY, algorithms=["EdDSA"])
    return {"vault_access": True, "sub": claims["sub"]}
