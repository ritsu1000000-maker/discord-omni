from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Operation:
    kind: str
    target_type: str
    target_id: str | None = None
    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def destructive(self) -> bool:
        return self.kind in {"delete", "remove"}

    def summary(self) -> str:
        target = self.metadata.get("name") or self.target_id or self.target_type
        return f"{self.kind.upper()} {self.target_type} {target}"


@dataclass
class EditPlan:
    guild_id: str
    operations: list[Operation] = field(default_factory=list)

    def add(self, operation: Operation):
        self.operations.append(operation)
        return operation

    @property
    def destructive_count(self):
        return sum(op.destructive for op in self.operations)

    def summaries(self):
        return [op.summary() for op in self.operations]

    def to_dict(self):
        return {
            "guild_id": self.guild_id,
            "destructive_count": self.destructive_count,
            "operations": [
                {
                    "kind": op.kind,
                    "target_type": op.target_type,
                    "target_id": op.target_id,
                    "before": op.before,
                    "after": op.after,
                    "metadata": op.metadata,
                }
                for op in self.operations
            ],
        }
