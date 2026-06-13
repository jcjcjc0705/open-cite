---
name: open-cite
description: Generate a formatted citation string (APA/IEEE/MLA) and BibTeX entry from a natural language description of one or more papers or books.
version: 3.1.0
metadata:
  hermes:
    tags: [citation, bibtex, apa, ieee, mla]
    category: utility
---

# Citation Formatter Skill

## When to Use

When the user describes one or more papers/books in natural language and wants formatted citations and BibTeX entries.

**Single paper:**
```
/open-cite LeCun 等人 1998 年在 Proceedings of the IEEE 卷86第11期發表的 Gradient-based learning applied to document recognition，頁2278-2324，DOI 10.1109/5.726791，請用 APA 格式
```

**Multiple papers:**
```
/open-cite 請用 APA 格式處理以下三篇文獻：
1. LeCun 等人 1998，Gradient-based learning，Proceedings of the IEEE, 86(11), 2278-2324
2. Vaswani 等人 2017，Attention is all you need，NeurIPS vol.30 pp.5998-6008
3. Goodfellow, Ian; Bengio, Yoshua，Deep Learning，MIT Press，2016
```

## Procedure

### Step 0 — Extract fields from natural language

Read the user's input and build a list of papers (a single paper is a list of length one). For each paper extract:

- `style`: look for "APA", "IEEE", "MLA" → default `APA` if not mentioned
- `entry_type`: infer from context
  - "journal" / "期刊" / has volume+number → `journal`
  - "conference" / "研討會" / venue is NeurIPS, CVPR, ICML, ICLR, ACL, EMNLP, etc. → `conference`
  - "book" / "書" / has publisher but no journal → `book`
  - default: `journal`
- `task_id`: assign `"cite_001"`, `"cite_002"`, … in order
- `author`: all author names in `Last, First` format, semicolon-separated
- `title`: exact title of the paper or book
- `year`: 4-digit year
- `journal` / `booktitle` / `publisher`: venue name matching `entry_type`
- `volume`, `number`, `pages`, `doi`: include if mentioned

**Do NOT guess or fabricate any field.** If a required field is not in the input, leave it absent.

### Step 1 — Process each paper and accumulate results

For EACH paper in the list (index `i = 0, 1, 2, …`):

1. Run `check_required`:
   ```
   python scripts/check_citation.py '{"mode":"check_required","style":"<style>","entry_type":"<entry_type>","fields":{...}}'
   ```
2. If `missing_required` is non-empty: append `{"task_id":...,"citation":"","bibtex":"","missing_fields":[...],"warning":"Missing required fields: <list>","confidence":0.0}` to results and **skip to the next paper**.
3. Otherwise: generate `citation` string (see Citation Format Rules below) and `bibtex` entry (see BibTeX Rules below).
4. Run `verify`:
   ```
   python scripts/check_citation.py '{"mode":"verify","style":"<style>","entry_type":"<entry_type>","fields":{...},"citation":"<citation>","bibtex":"<bibtex>"}'
   ```
   If `checks_failed > 0`, fix the reported issues and retry once.
5. Append `{"task_id":...,"style":...,"entry_type":...,"citation":...,"bibtex":...,"missing_fields":[],"warning":"","confidence":<0.8–1.0>}` to results.

### Step 2 — Emit all results at once

After the loop completes, call `run.py` **once** with the full list:
```
python scripts/run.py '{"results":[<item0>,<item1>,...]}'
```
**Copy the fenced JSON block verbatim as your final response. Add no text after it.**

---

## Citation Format Rules

### APA

*Journal:* `Author, F., & Author2, F. (Year). Title. *Journal*, *Vol*(No), pages. https://doi.org/DOI`
- Authors: `Last, Initials.`; use `&` before last author
- Article title: sentence case; journal name: title case, italicised

*Conference:* `Author, F. (Year). Title. In *Conference Name* (pp. pages).`

*Book:* `Author, F. (Year). *Title* (Edition ed.). Publisher.`

### IEEE

*Journal:* `F. Last and F. Last2, "Title," *Journal*, vol. V, no. N, pp. pages, Year.`
- Authors: `F. Last`; use `and` before last author; DOI appended as `, doi: DOI.`

*Conference:* `F. Last, "Title," in *Conference*, Year, pp. pages.`

*Book:* `F. Last, *Title*, Edition ed. City: Publisher, Year.`

### MLA

*Journal:* `Last, First, et al. "Title." *Journal*, vol. V, no. N, Year, pp. pages.`
- First author `Last, First`; subsequent authors `First Last`; `et al.` if >3 authors

*Conference:* `Last, First. "Title." *Conference*, Year, pp. pages.`

*Book:* `Last, First. *Title*. Edition ed., Publisher, Year.`

## BibTeX Rules

```bibtex
@<type>{<LastName><Year>,
  author = {<authors joined with " and ">},
  title  = {<title>},
  year   = {<year>},
  <type-specific fields>
}
```

Types: `journal→article`, `conference→inproceedings`, `book→book`

- `article`: + `journal, volume, number, pages` if present
- `inproceedings`: + `booktitle, pages` if present
- `book`: + `publisher, edition, address` if present
- Always include `doi = {<doi>}` if provided

## Pitfalls

- **Author format differs per style**: APA `Last, F.` / IEEE `F. Last` / MLA `Last, First` (first author only)
- **Sentence case**: APA article titles use sentence case; journal names use title case
- **Page ranges**: BibTeX uses `--` (`2278--2324`); formatted citations use `–` (en-dash)
- **Do not fabricate missing fields**: if a field is absent from the user's input, leave it missing
