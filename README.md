# open-cite

用自然語言描述論文或書籍，自動產生格式化引用字串與 BibTeX entry 的 Hermes skill。支援 APA、IEEE、MLA 三種格式，以及期刊論文、研討會論文、書籍三種類型。

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

### 呼叫方式

直接用自然語言描述所有文獻，一篇或多篇皆可：

```bash
hermes chat --toolsets skills,terminal --yolo -q '/open-cite 我想用 IEEE 格式，第一篇：LeCun 等人 1998 年在 Proceedings of the IEEE 卷86第11期發表的 Gradient-based learning applied to document recognition，頁2278-2324，DOI 10.1109/5.726791；第二篇：Vaswani 等人 2017，Attention is all you need，NeurIPS vol.30 pp.5998-6008'
```

### 輸出格式

```json
{
  "style": "IEEE",
  "count": 2,
  "citation": "[1] Y. LeCun, L. Bottou, and Y. Bengio, \"Gradient-based learning applied to document recognition,\" *Proceedings of the IEEE*, vol. 86, no. 11, pp. 2278–2324, 1998, doi: 10.1109/5.726791.\n[2] A. Vaswani et al., \"Attention is all you need,\" *Advances in Neural Information Processing Systems*, vol. 30, pp. 5998–6008, 2017.",
  "bibtex": "@article{LeCun1998,\n  author = {LeCun, Yann and Bottou, Leon and Bengio, Yoshua},\n  ...\n}\n\n@article{Vaswani2017,\n  author = {Vaswani, Ashish and ...},\n  ...\n}"
}
```

- `citation`：包含所有文獻、已編號的完整參考文獻清單，直接貼進論文
- `bibtex`：所有 BibTeX entry 合併在一起，貼進 `.bib` 檔即可

### 缺少必填欄位時

若任何一篇缺少必填資訊，skill **不會輸出結果**，而是用自然語言告知哪幾篇缺哪些欄位：

> 第一篇（Gradient-based learning）缺少：year
> 第三篇（Deep Learning）缺少：publisher
>
> 請補充以上資訊後我再繼續。

補充後繼續對話，skill 會重新處理所有文獻。


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
