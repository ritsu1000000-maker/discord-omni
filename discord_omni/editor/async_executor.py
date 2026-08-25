from __future__ import annotations
from .executor import ApplyResult
from .errors import ApplyError


async def _apply_one(client, guild_id, op, *, reason=None):
    api = client.official
    if op.target_type == "guild" and op.kind == "update":
        return await api.modify_guild(guild_id=guild_id, json=op.after, reason=reason)
    if op.target_type == "channel":
        if op.kind == "create":
            return await api.create_guild_channel(guild_id=guild_id, json=op.after, reason=reason)
        if op.kind == "update":
            return await api.modify_channel(channel_id=op.target_id, json=op.after, reason=reason)
        if op.kind == "delete":
            return await api.delete_channel(channel_id=op.target_id, reason=reason)
    if op.target_type == "role":
        if op.kind == "create":
            return await api.create_role(guild_id=guild_id, json=op.after, reason=reason)
        if op.kind == "update":
            return await api.modify_role(guild_id=guild_id, role_id=op.target_id, json=op.after, reason=reason)
        if op.kind == "move":
            return await api.modify_role_positions(guild_id=guild_id, json=[{"id": op.target_id, "position": op.after["position"]}], reason=reason)
        if op.kind == "delete":
            return await api.delete_role(guild_id=guild_id, role_id=op.target_id, reason=reason)
    raise ApplyError(f"unsupported operation: {op.kind} {op.target_type}")


async def apply_plan_async(client, plan, *, policy=None, dry_run=False, stop_on_error=True, reason=None):
    if policy is not None:
        policy.validate(plan)
    result = ApplyResult()
    for op in plan.operations:
        record = {"summary": op.summary(), "kind": op.kind, "target_type": op.target_type, "target_id": op.target_id}
        if dry_run:
            result.skipped.append({**record, "reason": "dry_run"})
            continue
        try:
            response = await _apply_one(client, plan.guild_id, op, reason=reason)
            result.applied.append({**record, "response": response})
        except Exception as exc:
            result.failed.append({**record, "error": f"{type(exc).__name__}: {exc}"})
            if stop_on_error:
                break
    return result
