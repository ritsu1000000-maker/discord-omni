#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="$(pwd)"
python -m unittest discover -s tests -v
