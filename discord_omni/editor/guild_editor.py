from __future__ import annotations
from .snapshot import fetch_snapshot, fetch_snapshot_async
from .mutator import SnapshotMutator
from .diff import build_plan
from .policy import EditorPolicy
from .executor import apply_plan
from .async_executor import apply_plan_async


class GuildEditor:
    def __init__(self, client, guild_id):
        self.client = client
        self.guild_id = str(guild_id)
        self.current = None
        self.desired = None

    def load(self, *, include_automod=True):
        self.current = fetch_snapshot(self.client, self.guild_id, include_automod=include_automod)
        self.desired = self.current.copy()
        return self

    @property
    def edit(self):
        if self.desired is None:
            raise RuntimeError("call load() first")
        return SnapshotMutator(self.desired)

    def plan(self):
        if self.current is None or self.desired is None:
            raise RuntimeError("call load() first")
        return build_plan(self.current, self.desired)

    def apply(self, *, policy=None, dry_run=False, reason=None, stop_on_error=True):
        plan = self.plan()
        if policy is None:
            policy = EditorPolicy()
        return apply_plan(self.client, plan, policy=policy, dry_run=dry_run, reason=reason, stop_on_error=stop_on_error)


class AsyncGuildEditor:
    def __init__(self, client, guild_id):
        self.client = client
        self.guild_id = str(guild_id)
        self.current = None
        self.desired = None

    async def load(self, *, include_automod=True):
        self.current = await fetch_snapshot_async(self.client, self.guild_id, include_automod=include_automod)
        self.desired = self.current.copy()
        return self

    @property
    def edit(self):
        if self.desired is None:
            raise RuntimeError("call load() first")
        return SnapshotMutator(self.desired)

    def plan(self):
        if self.current is None or self.desired is None:
            raise RuntimeError("call load() first")
        return build_plan(self.current, self.desired)

    async def apply(self, *, policy=None, dry_run=False, reason=None, stop_on_error=True):
        plan = self.plan()
        if policy is None:
            policy = EditorPolicy()
        return await apply_plan_async(self.client, plan, policy=policy, dry_run=dry_run, reason=reason, stop_on_error=stop_on_error)
