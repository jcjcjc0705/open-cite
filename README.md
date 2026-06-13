# open-cite

把文獻資訊轉成格式化引用字串與 BibTeX entry 的命令列工具。支援 APA、IEEE、MLA 三種格式，以及期刊論文、研討會論文、書籍三種類型。

## 需求

- Python 3.7 以上
- 不需要安裝任何套件（只使用標準函式庫）

## 快速開始

```bash
git clone https://github.com/jcjcjc0705/open-cite.git
cd open-cite
```

---

## 使用方式

### 產生單篇引用

呼叫 `scripts/run.py`，傳入一個 JSON 字串：

```bash
python scripts/run.py '{"task_id":"cite_001","style":"APA","entry_type":"journal","citation":"LeCun, Y., Bottou, L., & Bengio, Y. (1998). Gradient-based learning applied to document recognition. *Proceedings of the IEEE*, *86*(11), 2278–2324. https://doi.org/10.1109/5.726791","bibtex":"@article{LeCun1998,\n  author = {LeCun, Yann and Bottou, Leon and Bengio, Yoshua},\n  title  = {Gradient-based learning applied to document recognition},\n  journal = {Proceedings of the IEEE},\n  year   = {1998},\n  volume = {86},\n  number = {11},\n  pages  = {2278--2324},\n  doi    = {10.1109/5.726791}\n}","missing_fields":[],"warning":"","confidence":1.0}'
```

輸出：

````
```json
{
  "task_id": "cite_001",
  "style": "APA",
  "entry_type": "journal",
  "citation": "LeCun, Y., Bottou, L., & Bengio, Y. (1998). ...",
  "bibtex": "@article{LeCun1998, ...}",
  "missing_fields": [],
  "warning": "",
  "confidence": 1.0
}
```
````

---

### 產生多篇引用（batch 模式）

傳入帶有 `results` 陣列的 JSON：

```bash
python scripts/run.py '{"results":[
  {"task_id":"cite_001","style":"APA","entry_type":"journal","citation":"...","bibtex":"...","missing_fields":[],"warning":"","confidence":0.9},
  {"task_id":"cite_002","style":"IEEE","entry_type":"conference","citation":"...","bibtex":"...","missing_fields":[],"warning":"","confidence":0.9}
]}'
```

輸出為單一 JSON block，包含 `"results"` 陣列，每筆對應一篇文獻。

---

### 驗證引用是否完整（check_citation.py）

`check_citation.py` 提供兩種模式，不需要 LLM，純粹用來確認欄位與格式。

#### 模式 1：檢查必填欄位是否齊全

```bash
python scripts/check_citation.py '{"mode":"check_required","style":"APA","entry_type":"journal","fields":{"author":"LeCun, Yann","title":"Gradient-based learning","journal":"Proceedings of the IEEE","year":"1998"}}'
```

輸出：

```json
{
  "missing_required": [],
  "present_required": ["author", "title", "journal", "year"]
}
```

如果缺少欄位，`missing_required` 會列出來：

```bash
python scripts/check_citation.py '{"mode":"check_required","style":"APA","entry_type":"journal","fields":{"author":"LeCun, Yann","title":"Gradient-based learning"}}'
# → {"missing_required": ["journal", "year"], "present_required": ["author", "title"]}
```

#### 模式 2：驗證已生成的引用字串是否包含正確資訊

```bash
python scripts/check_citation.py '{"mode":"verify","style":"APA","entry_type":"journal","fields":{"author":"LeCun, Yann","title":"Gradient-based learning","journal":"Proceedings of the IEEE","year":"1998"},"citation":"LeCun, Y. (1998). Gradient-based learning. Proceedings of the IEEE.","bibtex":"@article{LeCun1998, author={LeCun, Yann}, title={Gradient-based learning}, journal={Proceedings of the IEEE}, year={1998}}"}'
```

輸出：

```json
{
  "checks_passed": 8,
  "checks_failed": 0,
  "failures": [],
  "all_passed": true
}
```

---

## 欄位說明

| 欄位 | 適用類型 | 必填 | 說明 |
|------|----------|------|------|
| `author` | 全部 | 是 | `姓, 名; 姓2, 名2`（分號分隔多位作者） |
| `title` | 全部 | 是 | 論文或書籍標題 |
| `year` | 全部 | 是 | 四位數年份 |
| `journal` | journal | 是 | 期刊名稱 |
| `booktitle` | conference | 是 | 研討會名稱 |
| `publisher` | book | 是 | 出版商 |
| `volume` | journal | 否 | 卷號 |
| `number` | journal | 否 | 期號 |
| `pages` | journal/conference | 否 | 頁碼，如 `100-110` |
| `doi` | 全部 | 否 | 不含 `https://doi.org/` 的 DOI 字串 |
| `edition` | book | 否 | 版次，如 `2nd` |
| `address` | book | 否 | 出版地 |

---

## 支援格式

| style | entry_type | 說明 |
|-------|-----------|------|
| `APA` | `journal` / `conference` / `book` | 美國心理學會格式 |
| `IEEE` | `journal` / `conference` / `book` | 電機電子工程師學會格式 |
| `MLA` | `journal` / `conference` / `book` | 現代語言學會格式 |

---

## 典型工作流程（寫論文時）

1. 建一個 `refs.json` 存放所有文獻的欄位資料
2. 用 `check_citation.py` 的 `check_required` 模式確認欄位齊全
3. 用 LLM（或自己手動）依格式規則生成 `citation` 與 `bibtex` 字串
4. 用 `check_citation.py` 的 `verify` 模式確認生成結果正確
5. 用 `run.py` 的 batch 模式輸出最終 JSON，從中取出 `citation`（貼進 Word）或 `bibtex`（貼進 `.bib` 檔）

---

## 授權

MIT License
