from __future__ import annotations

import json
import os
import re
from io import BytesIO
from typing import Any, Dict, List, Optional

from pypdf import PdfReader

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def _extract_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    pages = []
    for p in reader.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n\n".join(pages)


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _simple_heuristic_strategies(text: str) -> List[Dict[str, Any]]:
    # Very basic extraction: split by headings containing 'Strategy' or numbered sections
    chunks = re.split(r"(?i)\bstrategy\b|\n\s*\d+\.\s", text)
    items: List[Dict[str, Any]] = []
    idx = 1
    for ch in chunks:
        ch = ch.strip()
        if len(ch) < 25:
            continue
        # Title: first sentence up to 120 chars
        m = re.match(r"(.{10,120}?)([\.!?]|\n)", ch)
        title = (m.group(1) if m else ch[:80]).strip()
        # Description: next ~300 chars
        desc = ch[:400].strip()
        # KPIs: detect lines starting with KPI or bullet keywords
        kpi_match = re.findall(r"(?i)kpi[s]?:\s*([^\n]+)", ch)
        kpis = []
        for km in kpi_match:
            # split by separators
            kpis.extend([s.strip() for s in re.split(r"[,;]\s+", km) if s.strip()])
        items.append(
            {
                "id": f"S{idx}",
                "title": title,
                "description": desc,
                "kpis": kpis[:5],
                "priority": None,
            }
        )
        idx += 1
    return items


def _simple_heuristic_actions(text: str) -> List[Dict[str, Any]]:
    chunks = re.split(r"(?i)\baction\b|\n\s*\d+\.\s", text)
    items: List[Dict[str, Any]] = []
    idx = 1
    for ch in chunks:
        ch = ch.strip()
        if len(ch) < 25:
            continue
        m_title = re.match(r"(.{10,120}?)([\.!?]|\n)", ch)
        title = (m_title.group(1) if m_title else ch[:80]).strip()
        desc = ch[:300].strip()
        # owner: try to detect Owner: ... pattern
        owner = None
        m_owner = re.search(r"(?i)owner\s*[:\-]\s*([A-Za-z ]{2,40})", ch)
        if m_owner:
            owner = m_owner.group(1).strip()
        items.append(
            {
                "id": f"A{idx}",
                "title": title,
                "description": desc,
                "owner": owner or "Owner",
                "start_date": None,
                "end_date": None,
                "outputs": [],
            }
        )
        idx += 1
    return items


def _call_openai_for_json(kind: str, text: str) -> Optional[List[Dict[str, Any]]]:
    """Use OpenAI to extract structured JSON arrays. Returns None on failure."""
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["id", "title", "description"],
            },
        }
        if kind == "strategic":
            # add strategic fields
            schema["items"]["properties"].update(
                {
                    "kpis": {"type": "array", "items": {"type": "string"}},
                    "priority": {"type": ["string", "integer", "null"]},
                }
            )
        else:
            schema["items"]["properties"].update(
                {
                    "owner": {"type": "string"},
                    "start_date": {"type": ["string", "null"]},
                    "end_date": {"type": ["string", "null"]},
                    "outputs": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                }
            )

        system_prompt = "You extract structured JSON arrays. Output ONLY valid JSON."
        user_prompt = (
            f"Convert the following PDF text into a JSON array of {kind} entries. "
            "Use concise 'id' like S1/S2 or A1/A2. Include key fields.\n\n" + text
        )

        chat = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        raw = chat.choices[0].message.content
        if raw is None:
            return None

        data = json.loads(raw)
        # Basic validation
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return data
        return None
    except Exception:
        return None


def parse_strategic_pdf(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    text = _clean_text(_extract_text(pdf_bytes))
    data = _call_openai_for_json("strategic", text)
    if data:
        return data
    return _simple_heuristic_strategies(text)


def parse_action_pdf(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    text = _clean_text(_extract_text(pdf_bytes))
    data = _call_openai_for_json("action", text)
    if data:
        return data
    return _simple_heuristic_actions(text)
