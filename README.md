# open-cite

把文獻資訊轉成格式化引用字串與 BibTeX entry 的 Hermes skill。支援 APA、IEEE、MLA 三種格式，以及期刊論文、研討會論文、書籍三種類型。

## 需求

- Python 3.7 以上（不需額外安裝套件）
- [Hermes Agent](https://github.com/Netdb-NCKU/hermes-agent)（用來執行 skill）
- 任何 OpenAI-compatible LLM API（OpenAI、Ollama 本機模型等）

---

## 安裝步驟

### 1. 安裝 Hermes

```bash
pip install hermes-agent
```

確認安裝成功：

```bash
hermes --version
```

### 2. Clone 此 skill

```bash
git clone https://github.com/jcjcjc0705/open-cite.git
```

記下 clone 的資料夾路徑（例如 `/home/user/open-cite` 或 `C:\Users\user\open-cite`）。

### 3. 設定 LLM 提供者

建立 Hermes 設定檔 `~/.hermes/config.yaml`（Windows 為 `%APPDATA%\hermes\config.yaml`）。

根據你使用的 LLM 選擇以下任一範本：

#### OpenAI（GPT-4o 等）

```yaml
providers:
  - id: openai
    type: openai
    base_url: https://api.openai.com/v1
    key_env: OPENAI_API_KEY

models:
  - id: gpt-4o
    provider: openai
    model: gpt-4o

default_model: gpt-4o

skills:
  external_dirs:
    - /path/to/open-cite   # ← 改成你 clone 的上一層資料夾
```

在 `~/.hermes/.env` 加入：

```
OPENAI_API_KEY=sk-...
```

#### Ollama（本機模型，免費）

先安裝 [Ollama](https://ollama.com) 並下載模型：

```bash
ollama pull llama3.2
```

```yaml
providers:
  - id: ollama
    type: openai
    base_url: http://localhost:11434/v1
    key_env: OLLAMA_KEY

models:
  - id: llama3.2
    provider: ollama
    model: llama3.2

default_model: llama3.2

skills:
  external_dirs:
    - /path/to/open-cite   # ← 改成你 clone 的上一層資料夾
```

在 `~/.hermes/.env` 加入：

```
OLLAMA_KEY=ollama
```

#### 其他 OpenAI-compatible API

把 `base_url` 換成該服務的 endpoint，`key_env` 換成對應環境變數名稱即可，格式與上面相同。

---

> **`external_dirs` 路徑說明**
>
> `external_dirs` 必須指向 skill 資料夾的**上一層**，Hermes 會在該目錄下搜尋 `SKILL.md`。
>
> 例如 clone 到 `/home/user/open-cite`，那 `external_dirs` 填 `/home/user`；
> clone 到 `C:\Users\user\open-cite`，填 `C:\Users\user`。

---

## 使用方式

### 確認 skill 已載入

```bash
hermes skills list
```

應看到 `open-cite` 出現在清單中。

### 產生單篇引用

```bash
hermes chat --toolsets skills,terminal --yolo -q '/open-cite {
  "task_id": "cite_001",
  "style": "APA",
  "entry_type": "journal",
  "fields": {
    "author": "LeCun, Yann; Bottou, Leon; Bengio, Yoshua",
    "title": "Gradient-based learning applied to document recognition",
    "journal": "Proceedings of the IEEE",
    "year": "1998",
    "volume": "86",
    "number": "11",
    "pages": "2278-2324",
    "doi": "10.1109/5.726791"
  }
}'
```

輸出範例：

```json
{
  "task_id": "cite_001",
  "style": "APA",
  "entry_type": "journal",
  "citation": "LeCun, Y., Bottou, L., & Bengio, Y. (1998). Gradient-based learning applied to document recognition. *Proceedings of the IEEE*, *86*(11), 2278–2324. https://doi.org/10.1109/5.726791",
  "bibtex": "@article{LeCun1998,\n  author = {LeCun, Yann and Bottou, Leon and Bengio, Yoshua},\n  ...\n}",
  "missing_fields": [],
  "warning": "",
  "confidence": 0.95
}
```

- `citation`：直接貼進論文參考文獻（Word / 純文字）
- `bibtex`：貼進 `.bib` 檔，LaTeX 用 `\cite{LeCun1998}` 引用

### 一次處理多篇（batch）

```bash
hermes chat --toolsets skills,terminal --yolo -q '/open-cite {"citations":[
  {"task_id":"cite_001","style":"APA","entry_type":"journal","fields":{
    "author":"Vaswani, Ashish; Shazeer, Noam",
    "title":"Attention is all you need",
    "journal":"Advances in Neural Information Processing Systems",
    "year":"2017","volume":"30","pages":"5998-6008"
  }},
  {"task_id":"cite_002","style":"IEEE","entry_type":"conference","fields":{
    "author":"He, Kaiming; Zhang, Xiangyu",
    "title":"Deep residual learning for image recognition",
    "booktitle":"CVPR","year":"2016","pages":"770-778"
  }}
]}'
```

輸出為單一 JSON block，包含 `"results"` 陣列，每筆對應一篇文獻。

### 缺少必填欄位時

若輸入缺少必填欄位（例如 journal 缺 `year`），skill 會直接回報缺漏清單，不嘗試補全：

```json
{
  "citation": "",
  "bibtex": "",
  "missing_fields": ["year"],
  "warning": "Missing required fields: year",
  "confidence": 0.0
}
```

---

## 支援格式

| style | entry_type | 必填欄位 |
|-------|-----------|---------|
| `APA` / `IEEE` / `MLA` | `journal` | `author, title, journal, year` |
| `APA` / `IEEE` / `MLA` | `conference` | `author, title, booktitle, year` |
| `APA` / `IEEE` / `MLA` | `book` | `author, title, publisher, year` |

作者格式（`author` 欄位）：`姓, 名; 姓2, 名2`（分號分隔多位作者）

---

## 授權

MIT License
