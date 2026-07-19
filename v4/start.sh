#!/usr/bin/env bash
# Launches the tune.py + f3d workflow together: f3d opens (or reuses,
# once you build) --watch on the configured output STL in the background,
# tune.py runs in the foreground. Closing tune.py (q or Ctrl+C) also closes
# the f3d window it launched.
#
# Usage:
#   ./start.sh [config/blickensderfer.yaml]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CONFIG="${1:-config/blickensderfer.yaml}"

if [ ! -f "$CONFIG" ]; then
    echo "config file not found: $CONFIG" >&2
    exit 1
fi

if [ ! -d .venv ]; then
    echo ".venv not found - run the Setup steps in README.md first" >&2
    exit 1
fi
# shellcheck disable=SC1091
source .venv/bin/activate

OUT_DIR=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG'))['output']['directory'])")
OUT_NAME=$(python3 -c "import yaml; print(yaml.safe_load(open('$CONFIG'))['output']['stl_name'])")
OUT_PATH="$SCRIPT_DIR/$OUT_DIR/$OUT_NAME"
mkdir -p "$(dirname "$OUT_PATH")"

F3D_PID=""
if command -v f3d >/dev/null 2>&1; then
    if [ ! -f "$OUT_PATH" ]; then
        echo "note: $OUT_PATH doesn't exist yet - run a Preview/Full Build in the" \
             "tuner first, then use its 'Launch f3d' button (or re-run this script)."
    else
        f3d --watch "$OUT_PATH" -g -x >/dev/null 2>&1 &
        F3D_PID=$!
        echo "f3d --watch launched on $OUT_PATH (pid $F3D_PID)"
    fi
else
    echo "note: f3d not found on PATH - install it, or use the tuner's 'Launch f3d'" \
         "button once it's available." >&2
fi

cleanup() {
    if [ -n "$F3D_PID" ] && kill -0 "$F3D_PID" 2>/dev/null; then
        kill "$F3D_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

python3 tune.py "$CONFIG"
