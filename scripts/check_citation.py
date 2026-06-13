#!/usr/bin/env python3
"""
Citation checker for open-cite skill.

Two modes:

  mode=check_required
    Input:  {mode, style, entry_type, fields}
    Output: {missing_required: [...], present_required: [...]}

  mode=verify
    Input:  {mode, style, entry_type, fields, citation, bibtex}
    Output: {checks_passed, checks_failed, failures: [...], all_passed}

Usage:
    python check_citation.py '{"mode":"check_required","style":"APA","entry_type":"journal","fields":{...}}'
    python check_citation.py '{"mode":"verify","style":"APA","entry_type":"journal","fields":{...},"citation":"...","bibtex":"..."}'
"""

from __future__ import annotations

import json
import re
import sys

# Required fields per (style, entry_type) — same for all styles
REQUIRED = {
    "journal":    ["author", "title", "journal", "year"],
    "conference": ["author", "title", "booktitle", "year"],
    "book":       ["author", "title", "publisher", "year"],
}

BIBTEX_TYPE = {
    "journal": "article",
    "conference": "inproceedings",
    "book": "book",
}


def _emit(obj: dict) -> int:
    sys.stdout.write("```json\n")
    sys.stdout.write(json.dumps(obj, ensure_ascii=False, indent=2))
    sys.stdout.write("\n```\n")
    return 0


# ── check_required ────────────────────────────────────────────────────────────

def check_required(style: str, entry_type: str, fields: dict) -> dict:
    required = REQUIRED.get(entry_type, REQUIRED["journal"])
    missing = [f for f in required if not str(fields.get(f, "")).strip()]
    present = [f for f in required if str(fields.get(f, "")).strip()]
    return {"missing_required": missing, "present_required": present}


# ── verify ────────────────────────────────────────────────────────────────────

def _last_name(author_str: str) -> str:
    """Extract the first author's last name from 'Last, First; ...' format."""
    first = re.split(r"[;]|\band\b", author_str)[0].strip()
    # Handle "Last, First" or "First Last"
    if "," in first:
        return first.split(",")[0].strip()
    parts = first.split()
    return parts[-1] if parts else first


def _year_in(year: str, text: str) -> bool:
    return bool(year.strip()) and year.strip() in text


def _title_word_in(title: str, text: str) -> bool:
    """Check first significant word of title (>=4 chars) appears in text."""
    words = [w for w in re.findall(r"[A-Za-z]{4,}", title)]
    if not words:
        return title.strip().lower() in text.lower()
    return words[0].lower() in text.lower()


def _venue_in(venue: str, text: str) -> bool:
    """Check at least one significant word of the venue name appears."""
    words = [w for w in re.findall(r"[A-Za-z]{4,}", venue)]
    if not words:
        return venue.strip().lower() in text.lower()
    # Check first significant word
    return words[0].lower() in text.lower()


def _check_bibtex(entry_type: str, fields: dict, bibtex: str) -> list[str]:
    failures = []
    btype = BIBTEX_TYPE.get(entry_type, "article")
    if f"@{btype}" not in bibtex.lower():
        failures.append(f"bibtex: expected @{btype} entry type, not found")
    # Check key fields appear as bibtex field names
    required = REQUIRED.get(entry_type, REQUIRED["journal"])
    field_map = {"journal": "journal", "booktitle": "booktitle", "publisher": "publisher"}
    for f in required:
        val = str(fields.get(f, "")).strip()
        if not val:
            continue
        if f == "author":
            ln = _last_name(val)
            if ln.lower() not in bibtex.lower():
                failures.append(f"bibtex: author last name '{ln}' not found")
        elif f == "year":
            if val not in bibtex:
                failures.append(f"bibtex: year '{val}' not found")
        elif f == "title":
            words = [w for w in re.findall(r"[A-Za-z]{4,}", val)]
            if words and words[0].lower() not in bibtex.lower():
                failures.append(f"bibtex: title keyword '{words[0]}' not found")
        elif f in ("journal", "booktitle", "publisher"):
            words = [w for w in re.findall(r"[A-Za-z]{4,}", val)]
            if words and words[0].lower() not in bibtex.lower():
                failures.append(f"bibtex: venue keyword '{words[0]}' not found")
    return failures


def verify(style: str, entry_type: str, fields: dict, citation: str, bibtex: str) -> dict:
    failures = []
    required = REQUIRED.get(entry_type, REQUIRED["journal"])

    # Check citation string
    for f in required:
        val = str(fields.get(f, "")).strip()
        if not val:
            continue
        if f == "author":
            ln = _last_name(val)
            if ln.lower() not in citation.lower():
                failures.append(f"citation: author last name '{ln}' not found in citation")
        elif f == "year":
            if not _year_in(val, citation):
                failures.append(f"citation: year '{val}' not found in citation")
        elif f == "title":
            if not _title_word_in(val, citation):
                words = re.findall(r"[A-Za-z]{4,}", val)
                kw = words[0] if words else val[:10]
                failures.append(f"citation: title keyword '{kw}' not found in citation")
        elif f in ("journal", "booktitle", "publisher"):
            if not _venue_in(val, citation):
                words = re.findall(r"[A-Za-z]{4,}", val)
                kw = words[0] if words else val[:10]
                failures.append(f"citation: venue keyword '{kw}' not found in citation")

    # Check bibtex
    if bibtex.strip():
        failures += _check_bibtex(entry_type, fields, bibtex)

    total = len(required) * 2  # citation + bibtex checks per field
    passed = max(0, total - len(failures))
    return {
        "checks_passed": passed,
        "checks_failed": len(failures),
        "failures": failures,
        "all_passed": len(failures) == 0,
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    if len(argv) < 2:
        return _emit({"error": "usage: check_citation.py '<json>'"})
    try:
        payload = json.loads(argv[1])
    except json.JSONDecodeError as e:
        return _emit({"error": f"argv JSON invalid: {e}"})

    mode = str(payload.get("mode", "check_required"))
    style = str(payload.get("style", "APA")).upper()
    entry_type = str(payload.get("entry_type", "journal")).lower()
    fields = payload.get("fields") or {}

    if mode == "check_required":
        return _emit(check_required(style, entry_type, fields))
    elif mode == "verify":
        citation = str(payload.get("citation", ""))
        bibtex = str(payload.get("bibtex", ""))
        return _emit(verify(style, entry_type, fields, citation, bibtex))
    else:
        return _emit({"error": f"unknown mode: {mode!r}; use 'check_required' or 'verify'"})


if __name__ == "__main__":
    sys.exit(main(sys.argv))
