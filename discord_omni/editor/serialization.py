from __future__ import annotations
import json
from pathlib import Path
from .models import GuildSnapshot


def dumps(snapshot: GuildSnapshot, *, indent=2):
    return json.dumps(snapshot.to_dict(), indent=indent, ensure_ascii=False, sort_keys=True)


def loads(text: str):
    return GuildSnapshot.from_dict(json.loads(text))


def save(snapshot: GuildSnapshot, path):
    path = Path(path)
    path.write_text(dumps(snapshot) + "\n", encoding="utf-8")
    return path


def load(path):
    return loads(Path(path).read_text(encoding="utf-8"))
