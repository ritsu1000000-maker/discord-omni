class EditorError(RuntimeError):
    pass


class SnapshotError(EditorError):
    pass


class PlanError(EditorError):
    pass


class ApplyError(EditorError):
    pass


class PolicyError(EditorError):
    pass
