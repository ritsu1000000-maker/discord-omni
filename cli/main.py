from __future__ import annotations
import argparse
import json

from discord_omni import capabilities, power_feature_count, power_feature_names
from discord_omni.power_tools import find_routes, route_catalog


def cmd_info(_):
    print(json.dumps(capabilities(), indent=2, ensure_ascii=False))
    print("Power helpers:", power_feature_count())


def cmd_routes(args):
    data = route_catalog()
    if args.search:
        names = set(find_routes(args.search))
        data = [x for x in data if x["name"] in names]
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_features(args):
    names = power_feature_names()
    if args.search:
        q = args.search.lower()
        names = [x for x in names if q in x.lower()]
    for name in names:
        print(name)


def build_parser():
    parser = argparse.ArgumentParser(prog="discord-omni")
    sub = parser.add_subparsers(dest="command", required=True)

    info = sub.add_parser("info")
    info.set_defaults(func=cmd_info)

    routes = sub.add_parser("routes")
    routes.add_argument("--search")
    routes.set_defaults(func=cmd_routes)

    features = sub.add_parser("features")
    features.add_argument("--search")
    features.set_defaults(func=cmd_features)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
