#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

if ! command -v bruin >/dev/null 2>&1; then
  echo "Bruin CLI not found in PATH. Install with: curl -LsSf https://getbruin.com/install/cli | sh"
  exit 1
fi

echo "[1/4] Bruin version"
bruin version

echo "[2/4] Checking 'run' flags used in homework"
bruin run --help | grep -E -- "--downstream|--var|--full-refresh"

echo "[3/4] Checking lineage command"
bruin lineage --help | sed -n '1,40p'

echo "[4/4] Basic command check completed"
echo "Validated: --downstream, --var, --full-refresh, lineage"
