#!/usr/bin/env python3
"""
open-cite skill — final output wrapper.

Single mode (argv[1] is a plain object):
  {task_id, style, entry_type, citation, bibtex, missing_fields, warning, confidence}
  → emits a single fenced JSON block containing that object.

Batch mode (argv[1] has a "results" key whose value is a list):
  {"results": [{...}, {...}, ...]}
  → emits a single fenced JSON block containing {"results": [...]}.
"""

from __future__ import annotations

import json
import sys

VALID_STYLES = {"APA", "IEEE", "MLA"}
VALID_ENTRY_TYPES = {"journal", "conference", "book"}


def _clamp_confidence(v) -> float:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, f))


def _validate_one(obj: dict) -> dict:
    style = str(obj.get("style", "APA")).upper()
    if style not in VALID_STYLES:
        style = "APA"
    entry_type = str(obj.get("entry_type", "journal")).lower()
    if entry_type not in VALID_ENTRY_TYPES:
        entry_type = "journal"
    missing = obj.get("missing_fields")
    if not isinstance(missing, list):
        missing = []
    return {
        "task_id":        str(obj.get("task_id", "")),
        "style":          style,
        "entry_type":     entry_type,
        "citation":       str(obj.get("citation", "")),
        "bibtex":         str(obj.get("bibtex", "")),
        "missing_fields": [str(x) for x in missing],
        "warning":        str(obj.get("warning", "")),
        "confidence":     _clamp_confidence(obj.get("confidence", 0.5)),
    }


def emit_contract(obj: dict) -> int:
    sys.stdout.write("```json\n")
    sys.stdout.write(json.dumps(_validate_one(obj), ensure_ascii=False, indent=2))
    sys.stdout.write("\n```\n")
    return 0


def emit_batch(items: list) -> int:
    sys.stdout.write("```json\n")
    sys.stdout.write(json.dumps(
        {"results": [_validate_one(x) for x in items]},
        ensure_ascii=False, indent=2,
    ))
    sys.stdout.write("\n```\n")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        return emit_contract({
            "task_id": "", "style": "APA", "entry_type": "journal",
            "citation": "", "bibtex": "", "missing_fields": [],
            "warning": "run.py invoked without argv payload", "confidence": 0.0,
        })
    try:
        payload = json.loads(argv[1])
        if not isinstance(payload, dict):
            raise ValueError("payload not an object")
    except (json.JSONDecodeError, ValueError) as e:
        return emit_contract({
            "task_id": "", "style": "APA", "entry_type": "journal",
            "citation": "", "bibtex": "", "missing_fields": [],
            "warning": f"invalid argv JSON: {e}", "confidence": 0.0,
        })

    if "results" in payload and isinstance(payload["results"], list):
        return emit_batch(payload["results"])
    return emit_contract(payload)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
