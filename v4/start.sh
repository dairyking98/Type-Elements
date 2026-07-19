#!/usr/bin/env bash
# Launches tune.py. Does NOT auto-launch f3d - use the tuner's own
# "Launch f3d" button (or run f3d --watch yourself) once you've rendered
# at least once and want to see it.
#
# Usage:
#   ./start.sh                              # machine picker (choose Blickensderfer/Postal/...)
#   ./start.sh config/blickensderfer.yaml   # skip the picker, load directly

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d .venv ]; then
    echo ".venv not found - run the Setup steps in README.md first" >&2
    exit 1
fi
# shellcheck disable=SC1091
source .venv/bin/activate

if [ $# -eq 0 ]; then
    python3 tune.py
else
    CONFIG="$1"
    if [ ! -f "$CONFIG" ]; then
        echo "config file not found: $CONFIG" >&2
        exit 1
    fi
    python3 tune.py "$CONFIG"
fi
