from __future__ import annotations
from dataclasses import dataclass
from .errors import PolicyError
from .operations import EditPlan


@dataclass(slots=True)
class EditorPolicy:
    allow_delete_channels: bool = False
    allow_delete_roles: bool = False
    max_operations: int = 100
    max_destructive_operations: int = 0

    def validate(self, plan: EditPlan):
        if len(plan.operations) > self.max_operations:
            raise PolicyError(
                f"plan has {len(plan.operations)} operations; max={self.max_operations}"
            )

        destructive = [op for op in plan.operations if op.destructive]
        if len(destructive) > self.max_destructive_operations:
            raise PolicyError(
                f"plan has {len(destructive)} destructive operations; "
                f"max={self.max_destructive_operations}"
            )

        for op in destructive:
            if op.target_type == "channel" and not self.allow_delete_channels:
                raise PolicyError("channel deletion is disabled by policy")
            if op.target_type == "role" and not self.allow_delete_roles:
                raise PolicyError("role deletion is disabled by policy")

        return True
