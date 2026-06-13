---
name: open-cite
description: Generate a combined formatted reference list (APA/IEEE/MLA) and BibTeX block from a natural language description of one or more papers or books.
version: 4.0.0
metadata:
  hermes:
    tags: [citation, bibtex, apa, ieee, mla]
    category: utility
---

# Citation Formatter Skill

## When to Use

When the user describes one or more papers/books in natural language and wants a complete formatted reference list and BibTeX block.

**Example:**
```
/open-cite 我想用 IEEE 格式，第一篇：LeCun 等人 1998 年在 Proceedings of the IEEE 卷86第11期發表的 Gradient-based learning applied to document recognition，頁2278-2324；第二篇：Vaswani 等人 2017，Attention is all you need，NeurIPS vol.30 pp.5998-6008
```

## Procedure

### Step 1 — Extract fields from natural language

Read the user's input and build a list of papers. For each paper extract:

- `style`: look for "APA", "IEEE", "MLA" → default `APA` if not mentioned (applies to all papers)
- `entry_type`: infer from context
  - "journal" / "期刊" / has volume+number → `journal`
  - "conference" / "研討會" / venue is NeurIPS, CVPR, ICML, ICLR, ACL, EMNLP, etc. → `conference`
  - "book" / "書" / has publisher but no journal → `book`
  - default: `journal`
- `author`: all author names in `Last, First` format, semicolon-separated
- `title`: exact title of the paper or book
- `year`: 4-digit year
- `journal` / `booktitle` / `publisher`: venue name matching `entry_type`
- `volume`, `number`, `pages`, `doi`: include if mentioned

### Step 2 — Check for missing required fields

For EACH paper, run:
```
python scripts/check_citation.py '{"mode":"check_required","style":"<style>","entry_type":"<entry_type>","fields":{...}}'
```

Required fields per type (same for all styles):
- `journal`: author, title, journal, year
- `conference`: author, title, booktitle, year
- `book`: author, title, publisher, year

**If ANY paper has missing required fields:**
Do NOT proceed. Tell the user in natural language exactly which papers are missing which fields. For example:
> 第一篇（Gradient-based learning）缺少：year
> 第三篇（Deep Learning）缺少：publisher
>
> 請補充以上資訊後我再繼續。

Wait for the user to provide the missing information, then return to Step 1.

**Only proceed to Step 3 when ALL papers have all required fields.**

### Step 3 — Generate citation string and BibTeX entry for each paper

For each paper, generate:

**Citation string** — follow the format rules for the requested style:

*APA journal:* `Author, F., & Author2, F. (Year). Title. *Journal*, *Vol*(No), pages. https://doi.org/DOI`
- Authors: `Last, Initials.`; use `&` before last author; article title sentence case; journal italicised

*APA conference:* `Author, F. (Year). Title. In *Conference Name* (pp. pages).`

*APA book:* `Author, F. (Year). *Title* (Edition ed.). Publisher.`

*IEEE journal:* `F. Last and F. Last2, "Title," *Journal*, vol. V, no. N, pp. pages, Year[, doi: DOI].`
- Authors: `F. Last`; use `and` before last author

*IEEE conference:* `F. Last, "Title," in *Conference*, Year, pp. pages.`

*IEEE book:* `F. Last, *Title*, Edition ed. City: Publisher, Year.`

*MLA journal:* `Last, First, et al. "Title." *Journal*, vol. V, no. N, Year, pp. pages.`
- First author `Last, First`; subsequent `First Last`; `et al.` if >3 authors

*MLA conference:* `Last, First. "Title." *Conference*, Year, pp. pages.`

*MLA book:* `Last, First. *Title*. Edition ed., Publisher, Year.`

**BibTeX entry:**
```bibtex
@<type>{<LastName><Year>,
  author = {<authors joined with " and ">},
  title  = {<title>},
  year   = {<year>},
  <type-specific fields>
}
```
Types: `journal→article`, `conference→inproceedings`, `book→book`
Include `doi = {<doi>}` if provided.

### Step 4 — Verify each paper

For each paper, run:
```
python scripts/check_citation.py '{"mode":"verify","style":"<style>","entry_type":"<entry_type>","fields":{...},"citation":"<citation>","bibtex":"<bibtex>"}'
```
If `checks_failed > 0`, fix the reported issues and retry once.

### Step 5 — Combine and emit

Combine all individual results into:

- `combined_citation`: all citation strings joined with `\n`, each prefixed with `[1]`, `[2]`, … in order
- `combined_bibtex`: all BibTeX entries joined with `\n\n`

Then call `run.py` **once**:
```
python scripts/run.py '{"style":"<style>","count":<N>,"citation":"<combined_citation, newlines as \\n>","bibtex":"<combined_bibtex, newlines as \\n>"}'
```

**Copy the fenced JSON block verbatim as your final response. Add no text after it.**

## Pitfalls

- **Do not proceed past Step 2 if any field is missing** — ask the user first
- **Author format differs per style**: APA `Last, F.` / IEEE `F. Last` / MLA `Last, First` (first author only)
- **Sentence case**: APA article titles use sentence case; journal names use title case
- **Page ranges**: BibTeX uses `--` (`2278--2324`); formatted citations use `–` (en-dash)
- **Do not fabricate missing fields**: never guess a year, journal name, or author
