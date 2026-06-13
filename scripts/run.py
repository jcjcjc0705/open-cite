#!/usr/bin/env python3
"""
open-cite skill — final output wrapper.

Combined mode (argv[1] has "citation" and "bibtex" as top-level strings):
  {"style": "APA", "count": 3,
   "citation": "[1] ...\n[2] ...\n[3] ...",
   "bibtex": "@article{...}\n\n@article{...}\n\n@book{...}"}
  → emits a single fenced JSON block with combined reference list.
"""

from __future__ import annotations

import json
import sys

VALID_STYLES = {"APA", "IEEE", "MLA"}


def emit_combined(obj: dict) -> int:
    style = str(obj.get("style", "APA")).upper()
    if style not in VALID_STYLES:
        style = "APA"
    try:
        count = int(obj.get("count", 0))
    except (TypeError, ValueError):
        count = 0

    out = {
        "style":    style,
        "count":    count,
        "citation": str(obj.get("citation", "")),
        "bibtex":   str(obj.get("bibtex", "")),
    }
    sys.stdout.write("```json\n")
    sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=2))
    sys.stdout.write("\n```\n")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        return emit_combined({
            "style": "APA", "count": 0,
            "citation": "", "bibtex": "",
        })
    try:
        payload = json.loads(argv[1])
        if not isinstance(payload, dict):
            raise ValueError("payload not an object")
    except (json.JSONDecodeError, ValueError) as e:
        sys.stdout.write("```json\n")
        sys.stdout.write(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.stdout.write("\n```\n")
        return 1

    return emit_combined(payload)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
