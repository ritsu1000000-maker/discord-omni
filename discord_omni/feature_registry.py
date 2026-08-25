from __future__ import annotations
import inspect
from . import power_tools

def power_feature_names():
    return sorted(
        name for name, obj in vars(power_tools).items()
        if inspect.isfunction(obj) and obj.__module__ == power_tools.__name__ and not name.startswith("_")
    )

def power_feature_count():
    return len(power_feature_names())

def find_power_features(query):
    q = str(query).lower()
    return [name for name in power_feature_names() if q in name.lower()]
