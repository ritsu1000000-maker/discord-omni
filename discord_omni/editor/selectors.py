from __future__ import annotations


def _matches(obj, **criteria):
    for key, expected in criteria.items():
        actual = obj.get(key)
        if callable(expected):
            if not expected(actual):
                return False
        elif actual != expected:
            return False
    return True


def find_one(items, **criteria):
    matches = [x for x in items if _matches(x, **criteria)]
    if len(matches) > 1:
        raise LookupError(f"selector matched {len(matches)} items")
    return matches[0] if matches else None


def find_all(items, **criteria):
    return [x for x in items if _matches(x, **criteria)]


def by_id(items, object_id):
    sid = str(object_id)
    return next((x for x in items if str(x.get("id")) == sid), None)


def by_name(items, name):
    return [x for x in items if x.get("name") == name]
