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
    # Headless is configurable via env var UI_HEADLESS (default: false)
    ui_headless = os.environ.get("UI_HEADLESS", "").lower() in {"1", "true", "yes"}
    cmd.append(f"--server.headless={'true' if ui_headless else 'false'}")
    # Ensure app auto-runs sample alignment on startup
    env = os.environ.copy()
    # Silence ChromaDB telemetry to avoid noisy capture errors
    env.setdefault("CHROMADB_ANONYMIZED_TELEMETRY", "false")
    env.setdefault("ANONYMIZED_TELEMETRY", "false")
    env.setdefault("CHROMADB_DISABLE_TELEMETRY", "1")
    env.setdefault("CHROMADB_TELEMETRY_IMPLEMENTATION", "noop")
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
    env = os.environ.copy()
    env.setdefault("CHROMADB_ANONYMIZED_TELEMETRY", "false")
    env.setdefault("ANONYMIZED_TELEMETRY", "false")
    env.setdefault("CHROMADB_DISABLE_TELEMETRY", "1")
    env.setdefault("CHROMADB_TELEMETRY_IMPLEMENTATION", "noop")
    return subprocess.call(cmd, cwd=str(ROOT_DIR), env=env)


def run_build_graph() -> int:
    cmd = [
        sys.executable,
        str(ROOT_DIR / "scripts" / "build_graph.py"),
    ]
    print("Building RDF graph...\n", " ".join(cmd))
    env = os.environ.copy()
    env.setdefault("CHROMADB_ANONYMIZED_TELEMETRY", "false")
    env.setdefault("ANONYMIZED_TELEMETRY", "false")
    env.setdefault("CHROMADB_DISABLE_TELEMETRY", "1")
    env.setdefault("CHROMADB_TELEMETRY_IMPLEMENTATION", "noop")
    return subprocess.call(cmd, cwd=str(ROOT_DIR), env=env)


def run_query_graph() -> int:
    cmd = [
        sys.executable,
        str(ROOT_DIR / "scripts" / "query_graph.py"),
    ]
    print("Querying RDF graph...\n", " ".join(cmd))
    return subprocess.call(cmd, cwd=str(ROOT_DIR))


def run_evaluation() -> int:
    cmd = [
        sys.executable,
        str(ROOT_DIR / "scripts" / "run_evaluation.py"),
    ]
    print("Running evaluation metrics...\n", " ".join(cmd))
    env = os.environ.copy()
    env.setdefault("CHROMADB_ANONYMIZED_TELEMETRY", "false")
    env.setdefault("ANONYMIZED_TELEMETRY", "false")
    env.setdefault("CHROMADB_DISABLE_TELEMETRY", "1")
    env.setdefault("CHROMADB_TELEMETRY_IMPLEMENTATION", "noop")
    return subprocess.call(cmd, cwd=str(ROOT_DIR), env=env)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Strategy–Action Synchronization AI launcher"
    )
    sub = parser.add_subparsers(dest="command")

    ui = sub.add_parser("ui", help="Launch the Streamlit app (default)")
    ui.add_argument("--port", type=int, default=None, help="Streamlit server port")

    cli = sub.add_parser("cli", help="Run the CLI alignment script once")

    graph = sub.add_parser("graph", help="Build the RDF graph (TTL)")
    sub.add_parser("graph-query", help="Print graph counts and sample links")
    sub.add_parser("eval", help="Run evaluation (Precision/Recall/MAP/NDCG)")
    sub.add_parser("all", help="Run alignment, build graph, and evaluation")

    args = parser.parse_args(argv)

    # Maintenance/disable flag
    if os.getenv("DISABLE_ALL_SERVICES", "").lower() in {"1", "true", "yes"}:
        print("All services are disabled by administrator (DISABLE_ALL_SERVICES).")
        return 0

    if args.command in (None, "ui"):
        return run_ui(port=getattr(args, "port", None))
    elif args.command == "cli":
        return run_cli()
    elif args.command == "graph":
        return run_build_graph()
    elif args.command == "graph-query":
        return run_query_graph()
    elif args.command == "eval":
        return run_evaluation()
    elif args.command == "all":
        rc1 = run_cli()
        rc2 = run_build_graph()
        rc3 = run_evaluation()
        return 0 if (rc1 == 0 and rc2 == 0 and rc3 == 0) else 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
