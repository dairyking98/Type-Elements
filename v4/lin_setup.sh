#!/usr/bin/env bash
# Creates/updates the .venv that start.sh runs against - run this once,
# and again any time requirements.txt changes.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -r requirements.txt

echo "Setup complete - run ./start.sh to launch tune.py"
