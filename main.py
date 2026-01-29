from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).resolve().parent


def run_ui(port: int | None = None) -> int:
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ROOT_DIR / "app" / "streamlit_app.py"),
    ]
    # Default port 8504 if not provided
    if port is None:
        port = 8504
    cmd.append(f"--server.port={port}")
    # Prefer headless to avoid auto browser pops in some environments
    cmd.append("--server.headless=true")
    # Ensure app auto-runs sample alignment on startup
    env = os.environ.copy()
    env.setdefault("AUTO_RUN_SAMPLE", "1")
    print("Starting Streamlit UI...\n", " ".join(cmd))
    return subprocess.call(cmd, cwd=str(ROOT_DIR), env=env)


def run_cli() -> int:
    # Delegate to the existing CLI runner to avoid duplication
    cmd = [
        sys.executable,
        str(ROOT_DIR / "scripts" / "run_alignment.py"),
    ]
    print("Running CLI alignment...\n", " ".join(cmd))
    return subprocess.call(cmd, cwd=str(ROOT_DIR))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Strategy–Action Synchronization AI launcher"
    )
    sub = parser.add_subparsers(dest="command")

    ui = sub.add_parser("ui", help="Launch the Streamlit app (default)")
    ui.add_argument("--port", type=int, default=None, help="Streamlit server port")

    cli = sub.add_parser("cli", help="Run the CLI alignment script once")

    args = parser.parse_args(argv)

    # Maintenance/disable flag
    if os.getenv("DISABLE_ALL_SERVICES", "").lower() in {"1", "true", "yes"}:
        print("All services are disabled by administrator (DISABLE_ALL_SERVICES).")
        return 0

    if args.command in (None, "ui"):
        return run_ui(port=getattr(args, "port", None))
    elif args.command == "cli":
        return run_cli()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
