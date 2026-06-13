---
name: open-cite
description: Generate a formatted citation string (APA/IEEE/MLA) and BibTeX entry from natural language or structured JSON input.
version: 2.0.0
metadata:
  hermes:
    tags: [citation, bibtex, apa, ieee, mla]
    category: utility
---

# Citation Formatter Skill

## When to Use

When the user wants a formatted citation string and BibTeX entry. Accepts **natural language**, **structured JSON**, or **a mix of both** for batch requests.

**Natural language (single paper):**
```
/open-cite LeCun 等人 1998 年在 Proceedings of the IEEE 卷86第11期發表的 Gradient-based learning applied to document recognition，頁2278-2324，DOI 10.1109/5.726791，請用 APA 格式
```

```
/open-cite APA format: Vaswani, Ashish et al., "Attention is all you need", NeurIPS 2017, vol. 30, pp. 5998-6008
```

**Structured JSON (single paper):**
```
/open-cite {"style":"APA","entry_type":"journal","fields":{
  "author":"LeCun, Yann; Bottou, Leon; Bengio, Yoshua",
  "title":"Gradient-based learning applied to document recognition",
  "journal":"Proceedings of the IEEE",
  "year":"1998","volume":"86","number":"11","pages":"2278-2324","doi":"10.1109/5.726791"
}}
```

**Multiple papers (batch, natural language or JSON):**
```
/open-cite 請用 APA 格式處理以下三篇文獻：
1. LeCun 等人 1998，Gradient-based learning，Proceedings of the IEEE, 86(11), 2278-2324
2. Vaswani 等人 2017，Attention is all you need，NeurIPS vol.30 pp.5998-6008
3. Goodfellow 等人，Deep Learning，MIT Press，2016
```

## Field Reference

| Field | Used by | Notes |
|---|---|---|
| `author` | all | Semicolon-separated: `Last, First; Last2, First2` |
| `title` | all | Title of the work |
| `year` | all | 4-digit year |
| `journal` | journal | Journal name |
| `booktitle` | conference | Conference name |
| `publisher` | book | Publisher name |
| `volume` | journal | Volume number |
| `number` | journal | Issue number |
| `pages` | journal/conference | e.g. `100-110` or `100--110` |
| `doi` | all (optional) | DOI string without `https://doi.org/` prefix |
| `edition` | book (optional) | e.g. `2nd` |
| `address` | book (optional) | Publisher city |

## Procedure

Follow every step in order.

### Step 0 — Parse input and detect mode

**Determine input type:**

- **Natural language**: the input is free text (not a JSON object). Extract all bibliographic information from the text (see extraction rules below), then continue with Steps 1–5 using the extracted fields.
- **Structured JSON with `"citations"` key**: the value is a list → follow the **Batch Procedure** below.
- **Structured JSON without `"citations"` key**: extract `task_id`, `style`, `entry_type`, `fields` directly, then continue with Steps 1–5.

**Natural language extraction rules:**

Extract the following from the text:
- `style`: look for "APA", "IEEE", "MLA" (default: `APA` if not mentioned)
- `entry_type`: infer from context — "journal"/"期刊" → `journal`; "conference"/"研討會"/"proceedings"/"NeurIPS"/"CVPR"/"ICML" etc. → `conference`; "book"/"書" → `book` (default: `journal`)
- `task_id`: generate as `"cite_001"` if not provided
- `fields.author`: extract all author names, convert to `Last, First` format separated by semicolons. If input says "LeCun 等人" or "et al." with only one name, use what is given and note others are unknown.
- `fields.title`: the title of the paper/book
- `fields.year`: 4-digit year
- `fields.journal` / `fields.booktitle` / `fields.publisher`: venue name depending on entry_type
- `fields.volume`, `fields.number`, `fields.pages`, `fields.doi`: if mentioned

**If multiple papers are described in natural language**, treat as batch: extract each paper's fields independently, then follow the **Batch Procedure**.

**If a required field cannot be extracted**, do NOT guess or fabricate it. Leave it missing; `check_citation.py` will report it in `missing_required`.

If `style` or `entry_type` is missing after extraction, use defaults: `style=APA`, `entry_type=journal`.

---

#### Batch Procedure (run this instead of Steps 1–5 when `citations` key is present)

For EACH item in `citations` (iterate index `i = 0, 1, 2, …`):

1. Extract `task_id`, `style`, `entry_type`, `fields` from the item (apply the same defaults as single mode).
2. Run `check_required`:
   ```
   python scripts/check_citation.py '{"mode":"check_required","style":"<style>","entry_type":"<entry_type>","fields":{...}}'
   ```
3. If `missing_required` is non-empty: add to results as `{"task_id":...,"citation":"","bibtex":"","missing_fields":[...],"warning":"Missing required fields: <list>","confidence":0.0}`. Skip to next item.
4. Otherwise: generate `citation` string and `bibtex` entry (follow the style rules in Steps 2–3 of the single procedure).
5. Run `verify`:
   ```
   python scripts/check_citation.py '{"mode":"verify","style":"<style>","entry_type":"<entry_type>","fields":{...},"citation":"<citation>","bibtex":"<bibtex>"}'
   ```
   If `checks_failed > 0`, fix once and re-verify.
6. Add `{"task_id":...,"style":...,"entry_type":...,"citation":...,"bibtex":...,"missing_fields":[],"warning":"","confidence":<0.8–1.0>}` to the results list.

After processing ALL items, call run.py **once** with the full results array:
```
python scripts/run.py '{"results":[<item0>,<item1>,...]}'
```
Copy the fenced JSON block verbatim as your final response. Add no text after it.

---

### Step 1 — Check required fields

Run:

```
python scripts/check_citation.py '{"mode":"check_required","style":"<style>","entry_type":"<entry_type>","fields":{...}}'
```

The script returns `{"missing_required": [...], "present_required": [...]}`.

- If `missing_required` is non-empty: emit the contract immediately with `citation=""`, `bibtex=""`, `missing_fields=<list>`, `warning="Missing required fields: <list>"`, `confidence=0.0`. **Do not attempt to generate a citation.**
- If `missing_required` is empty: proceed to Step 2.

### Step 2 — Format the citation string

Using the fields provided, generate a formatted citation string following the style rules below.

**APA format:**

*Journal:*
`Author, F., & Author2, F. (Year). Title of article. *Journal Name*, *Volume*(Number), pages. https://doi.org/DOI`

- Author format: `Last, Initials.` — e.g. `LeCun, Y., Bottou, L., & Bengio, Y.`
- Use `&` before last author (if >1 author)
- Year in parentheses
- Article title: sentence case (only first word and proper nouns capitalised)
- Journal name: *italicised* (use asterisks in plain text: `*Journal Name*`)
- Volume italicised, issue in regular parentheses
- DOI as full URL: `https://doi.org/...` (omit if not provided)

*Conference:*
`Author, F. (Year). Title. In *Proceedings of Conference Name* (pp. pages). Publisher.`

*Book:*
`Author, F. (Year). *Title* (Edition ed.). Publisher.`

**IEEE format:**

*Journal:*
`F. Author, F. Author2, and F. Author3, "Title of article," *Journal Name*, vol. Volume, no. Number, pp. pages, Year.`

- Author format: `F. Last` — e.g. `Y. LeCun, L. Bottou, and Y. Bengio`
- Use `and` before last author
- Title in double quotes
- Journal name italicised
- DOI appended as: `, doi: DOI.` (omit if not provided)

*Conference:*
`F. Author, "Title," in *Conference Name*, Year, pp. pages.`

*Book:*
`F. Author, *Title*, Edition ed. City: Publisher, Year.`

**MLA format:**

*Journal:*
`Last, First, et al. "Title." *Journal Name*, vol. Volume, no. Number, Year, pp. pages.`

- First author: `Last, First` — subsequent authors: `First Last`
- Use `et al.` if more than 3 authors
- Title in double quotes; journal italicised

*Conference:*
`Last, First. "Title." *Conference Name*, Year, pp. pages.`

*Book:*
`Last, First. *Title*. Edition ed., Publisher, Year.`

### Step 3 — Generate BibTeX entry

Generate a BibTeX entry using this structure:

```bibtex
@<bibtex_type>{<key>,
  author    = {<full author names joined with " and ">},
  title     = {<title>},
  <type-specific fields>,
  year      = {<year>}
}
```

BibTeX entry types: `journal→article`, `conference→inproceedings`, `book→book`.

Citation key: `<LastName><Year>` — e.g. `LeCun1998`.

Required BibTeX fields per type:
- `article`: `author, title, journal, year` (+ `volume, number, pages` if present)
- `inproceedings`: `author, title, booktitle, year` (+ `pages` if present)
- `book`: `author, title, publisher, year` (+ `edition, address` if present)

Include `doi = {<doi>}` if provided.

### Step 4 — Verify output

Run:

```
python scripts/check_citation.py '{"mode":"verify","style":"<style>","entry_type":"<entry_type>","fields":{...},"citation":"<citation>","bibtex":"<bibtex>"}'
```

The script checks that field values appear in the outputs. If `checks_failed > 0`, read `failures` and fix the specific issues. Retry once.

### Step 5 — Emit the contract

Run:

```
python scripts/run.py '<json>'
```

where `<json>` is:

```json
{
  "task_id": "<id>",
  "style": "<style>",
  "entry_type": "<entry_type>",
  "citation": "<formatted citation string>",
  "bibtex": "<bibtex entry string, newlines as \\n>",
  "missing_fields": [],
  "warning": "",
  "confidence": <0.0-1.0>
}
```

**Copy the fenced JSON block from `run.py` verbatim as your final response. Add no text after it.**

## Pitfalls

- **Author name format differs per style**: APA uses `Last, F.`, IEEE uses `F. Last`, MLA uses `Last, First` for first author only.
- **Sentence case vs Title Case**: APA article titles use sentence case; journal names use title case. IEEE and MLA use title case for titles.
- **En-dash in pages**: BibTeX uses `--` for page ranges (`2278--2324`); formatted citations use `–` (en-dash).
- **Missing fields are not an error to retry**: if `check_citation.py` reports missing required fields in mode=`check_required`, emit immediately with empty citation — do not attempt to fill in missing values.
- **JSON escaping**: newlines in `bibtex` must be `\\n` inside the JSON argument string.
