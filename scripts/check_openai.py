from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    # Load env from .env if present
    load_dotenv(ROOT / ".env")

    api_key = os.getenv("OPENAI_API_KEY")
    model = "gpt-4o-mini"

    if not api_key:
        print("OPENAI_API_KEY is NOT set.")
        return 2

    try:
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "ping"}],
        )
        print(
            f"OpenAI connectivity: OK | model={model} | completion_id={getattr(resp, 'id', 'n/a')}"
        )
        return 0
    except Exception as e:
        print(
            f"OpenAI connectivity: FAILED | model={model} | error={e.__class__.__name__}: {e}"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
