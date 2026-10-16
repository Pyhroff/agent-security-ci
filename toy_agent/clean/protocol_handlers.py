"""
Clean (CEGIS-Hardened) Formal Protocol Handlers for `specprove-sec` CI Regression Gate.
All handlers enforce formal Z3 safety invariants (MCP-01, MCP-02, ZTA-01).
"""

from typing import Any, Dict


def dispatch_mcp_admin_tool(orchestrator: Any, req: Any, tool_fn: Any) -> Any:
    """[MCP-01 Hardened] Intersects orchestrator.ambient_cap with req.caller_bound_cap."""
    if min(orchestrator.ambient_cap, req.caller_bound_cap) >= req.required_cap:
        return tool_fn(req.arguments)
    raise PermissionError("Insufficient delegated capability")


def execute_registered_mcp_tool(tool: Any, payload: Dict[str, Any]) -> Any:
    """[MCP-02 Hardened] Enforces cryptographic schema digest pinning before tool invocation."""
    if tool.user_approved and tool.live_schema_hash == tool.pinned_schema_hash:
        return tool.invoke(tool.live_schema, payload)
    raise PermissionError("Tool unapproved or schema hash drifted")


def verify_zero_trust_vault_request(
    jwt: Any, token: str, IDP_PUBKEY: str, VAULT_SERVICE_ID: str
) -> Dict[str, Any]:
    """[ZTA-01 Hardened] Strictly binds audience=VAULT_SERVICE_ID on JWT verification."""
    claims = jwt.decode(
        token, IDP_PUBKEY, audience=VAULT_SERVICE_ID, algorithms=["EdDSA"]
    )
    return {"vault_access": True, "sub": claims["sub"]}
