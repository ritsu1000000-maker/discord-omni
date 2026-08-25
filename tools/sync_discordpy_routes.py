r"""
Extract Discord REST Route(...) usages from a local checkout of Rapptz/discord.py.

Usage:
    python tools/sync_discordpy_routes.py C:\path\to\discord.py

This does NOT use private Discord APIs. It only scans source code you already
have locally and emits a JSON inventory for review.
"""
from __future__ import annotations
import ast
import json
import sys
from pathlib import Path

FILES = [
    Path("discord/http.py"),
    Path("discord/webhook/async_.py"),
    Path("discord/webhook/sync.py"),
]

def literal(node):
    try:
        return ast.literal_eval(node)
    except Exception:
        return None

def scan_file(path: Path):
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        is_route = isinstance(fn, ast.Name) and fn.id == "Route"
        if not is_route:
            continue
        if len(node.args) < 2:
            continue
        method = literal(node.args[0])
        route = literal(node.args[1])
        if isinstance(method, str) and isinstance(route, str):
            found.append({"method": method, "path": route, "source": str(path)})
    return found

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python tools/sync_discordpy_routes.py PATH_TO_DISCORDPY")
    repo = Path(sys.argv[1]).resolve()
    all_routes = []
    for rel in FILES:
        path = repo / rel
        if path.exists():
            all_routes.extend(scan_file(path))
    unique = {}
    for item in all_routes:
        unique[(item["method"], item["path"])] = item
    data = sorted(unique.values(), key=lambda x: (x["path"], x["method"]))
    out = Path("discordpy-route-snapshot.json")
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {len(data)} unique routes to {out}")

if __name__ == "__main__":
    main()
