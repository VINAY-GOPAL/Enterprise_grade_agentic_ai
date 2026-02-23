#!/usr/bin/env python
"""Invoke agent with payload from file. Use to avoid PowerShell/CLI argument splitting.

Usage:
    uv run python scripts/invoke_with_payload.py payload.json
    uv run python scripts/invoke_with_payload.py payload_electric_cars.json --session-id <id>
"""
import json
import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    payload_path = Path(sys.argv[1])
    if not payload_path.exists():
        print(f"Error: {payload_path} not found", file=sys.stderr)
        sys.exit(1)
    payload_str = payload_path.read_text(encoding="utf-8").strip()
    try:
        json.loads(payload_str)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {payload_path}: {e}", file=sys.stderr)
        sys.exit(1)
    args = ["agentcore", "invoke", payload_str] + sys.argv[2:]
    subprocess.run(args, cwd=Path(__file__).resolve().parent.parent)


if __name__ == "__main__":
    main()
