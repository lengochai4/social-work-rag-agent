# Social Work (CTXH) Assistant: Point Conversion & Registration

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 15 Passed](https://img.shields.io/badge/tests-15%20passed-brightgreen.svg)](tests/)

An AI Agent system developed for Ho Chi Minh City University of Technology and Education (**HCMUTE**) to automate Social Work (**Công tác xã hội - CTXH**) inquiries, point/day conversions, graduation eligibility checks, and verified activity registrations.

Topic **T5** - Advanced AI & RAG Agent Final Project (**AIPR**).

---

##  1. Quick Start (Evaluator One-Liner)

### Linux / macOS / WSL:
```bash
make setup && make demo
make eval
make test
```

### Windows (CMD or PowerShell):
The repository includes a native `make.bat` wrapper so you can run `make` commands on Windows without installing any third-party tools:
- **Command Prompt (CMD)**:
  ```cmd
  make setup
  make demo
  make eval
  make test
  ```
- **PowerShell**:
  ```powershell
  .\make demo
  .\make eval
  .\make test
  ```
- **Direct Python commands** (platform independent):
  ```bash
  python run_demo.py
  python run_evaluation.py
  pytest tests/ -v
  ```

LINK DATA: https://drive.google.com/drive/folders/1VCwrwHplQBLwjCfr_11-UZMcpYLjV4zI?hl=vi
---

##  2. The 3 Mandatory Architecture Layers

This project strictly adheres to the 3-layer architecture required by the project specifications:

### 1. Grounded Retrieval Layer (RAG with Evidence)
- **Hybrid Search**: Combines Lexical BM25 (`rank-bm25` with Vietnamese tokenization and administrative stopword removal) and Dense Semantic Search (`intfloat/multilingual-e5-base`, 768-dim embeddings).
- **Evidence Citation**: Every response cites exact sources with `doc_id`, `chunk_id`, and title (from HCMUTE Decision 224/QĐ-ĐHSPKT-CTHSSV 2013 and Student Handbook 2024).
- **Calibration Refusal (`threshold = 0.55`)**: Domain concept verification and score calibration automatically identify and reject out-of-domain queries (e.g., Bitcoin prices, MongoDB setup, weather) with standard rejection phrase: *"Tôi chưa tìm thấy đủ căn cứ trong tài liệu hiện có để trả lời câu hỏi này (no_answer)."*

### 2. Transformation Layer (Reasoning & Computation)
- **Conversion Rule**: Converts points to days using the official regulation ratio (**10 CTXH points = 1 CTXH day**; special campaigns such as Green Summer award up to 4 days).
- **Graduation Assessment**: Compares cumulative semester points against HCMUTE graduation threshold (**40 CTXH points / 4 CTXH days**).
- **Shortfall Calculation**: Automatically calculates remaining points required if a student has not yet met graduation criteria.

### 3. Action & Verify Layer (ReAct Agent & MCP Server)
- **Model Context Protocol (MCP)**: Operates over clean `stdio` transport. Strict stdout purity (strictly JSON-RPC on `stdout`; all logging routed to `sys.stderr`).
- **Side-Effect Tool (`register_activity`)**: Awards points and mutates student state in persistent JSON database (`data/db/ctxh_db.json`).
- **Mandatory Verification (`get_status`)**: Enforces the **Action & Verify** constraint within the handwritten ReAct loop (`MAX_STEPS = 10`). After mutating state, the Agent is strictly required to call `get_status` to observe real database changes before formulating the final answer.

---

##  3. Project Structure

```text
social-work-rag-agent/
├── Makefile                     # Automation targets for Linux/macOS/WSL
├── make.bat                     # Automation wrapper for Windows (CMD and PowerShell)
├── README.md                    # System documentation and instructions
├── ai-usage.md                  # Academic integrity disclosure (AI usage disclosure)
├── config.py                    # Project configurations, paths, model settings
├── requirements.txt             # Clean, minimal project dependencies
├── pytest.ini                   # Pytest configuration
├── run_demo.py                  # End-to-end live demo script (3 layers: Retrieve -> Compute -> Action & Verify)
├── run_evaluation.py            # Benchmark script (make eval: evaluates 12 queries, logs tokens, generates chart)
├── data/
│   ├── processed/               # Cleaned HCMUTE regulation documents (Markdown)
│   ├── ctxh_chunks.json         # 78 curated regulation chunks
│   ├── ctxh_embeddings.json     # Precomputed dense vector embeddings (intfloat/multilingual-e5-base)
│   └── db/
│       ├── ctxh_db.json         # Student profiles and accumulated point records
│       └── ctxh_db.seed.json    # Seed database for reproducible demo runs
├── prompts/                     # Separated prompt templates
│   ├── agent_system.txt         # System prompt for ReAct Agent loop
│   ├── rag_system.txt           # System prompt for RAG Generator
│   └── rag_user.txt             # Query augmentation template
├── src/
│   ├── main.py                  # Interactive CLI entrypoint
│   ├── schemas.py               # Data schemas declared with @dataclass & type hints
│   ├── llm_client.py            # API client with Exponential Backoff + Jitter & TokenUsage tracker
│   ├── retrieval/               # HybridSearch (BM25 + Dense E5), Embedder, and Calibration
│   ├── rag/                     # Context augmentation and cited response generation
│   ├── agent/                   # Handwritten ReAct agent loop (MAX_STEPS = 10, Action & Verify)
│   └── mcp/                     # MCP Server (stdio transport, clean stdout, dynamic discovery, interop client)
├── tests/
│   ├── testset.jsonl            # 12 test questions (8 in-domain HCMUTE queries, 4 no_answer queries)
│   ├── test_retrieval.py        # Unit tests for Hybrid Search, Normalization, Calibration & Metadata filters
│   ├── test_mcp.py              # Unit tests for MCP stdio handshake, tools discovery, state mutation & interop
│   └── test_agent.py            # Unit tests for TokenUsage, prompt templates, and database integrity
├── results/                     # Evaluation summaries, CSV logs, and visualization charts
│   ├── evaluation_summary.json  # Benchmark summary JSON
│   ├── eval_results.csv         # Detailed per-question metrics (tokens, latency, scores)
│   ├── eval_chart.png           # Visualization chart (calibration scores & token usage)
│   └── ablation_study.json      # Dense-Only vs Hybrid Search ablation metrics
└── logs/                        # Historical JSONL run logs with per-question USAGE metrics
```

---

##  4. Evaluation Benchmarks

Run via `make eval` (or `python run_evaluation.py`):

| Metric | Result | Benchmark Target | Status |
| :--- | :---: | :---: | :---: |
| **Overall Accuracy** | **100.0%** (12/12) | $\ge 90\%$ | Passed |
| **Rejection Rate (`no_answer`)** | **100.0%** (4/4) | $\ge 90\%$ | Passed |
| **In-Domain Retrieval Accuracy** | **100.0%** (8/8) | $\ge 90\%$ | Passed |
| **Average Latency** | **1.2s - 2.4s** | $< 5.0\text{s}$ | Passed |
| **Token Usage Tracking** | 100% logged per question | Calls, Prompt, Completion, Max | Logged |

### Ablation Study: Dense-Only vs. Hybrid Search
| Configuration | Avg In-Domain Score | Avg Out-of-Domain Score | Rejection Accuracy at Threshold (0.55) |
| :--- | :---: | :---: | :---: |
| **Dense-Only** (`multilingual-e5-base`) | 0.8651 | 0.7887 | 75.0% *(False positives on out-of-domain terms)* |
| **Hybrid Search** (BM25 + Dense E5) | **0.9321** | **0.3155** | **100.0%** *(Clear separation, safe refusal)* |

---

##  5. Bonus Criteria Implemented (+4 Points)

1. **Real Metadata Filtering (`+1 pt`)**:
   - `HybridSearch.search(..., filter_metadata={"doc_id": "CTXH_001"})` filters candidate chunks by document version/ID prior to ranking.
2. **Ablation Study Configuration (`+1 pt`)**:
   - Evaluates Dense-Only vs Hybrid Search automatically and saves metrics to `results/ablation_study.json`.
3. **Data Visualizations & CSV Export (`+1 pt`)**:
   - Exports detailed per-query metrics to `results/eval_results.csv` and renders a dual-panel chart to `results/eval_chart.png`.
4. **Second Client Interoperability (`+1 pt`)**:
   - `src/mcp/second_client.py` provides an independent secondary client process connecting to the MCP Server over `stdio` to prove cross-process interoperability.

---

##  6. Running Unit Tests

```bash
make test
```

Executes 15 comprehensive tests covering retrieval, calibration, MCP communication, and agent integrity.

---

##  7. Environment Variables

Create a `.env` file in the project root:

```bash
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-20b
GROQ_API_KEY=your_groq_api_key_here
LLM_TIMEOUT=30
LLM_MAX_RETRIES=5
LLM_BASE_DELAY=1
LLM_MAX_DELAY=30
```

---

##  Academic Integrity & AI Usage

In compliance with project guidelines, all AI assistance is transparently documented in [ai-usage.md](ai-usage.md). All core algorithms, schemas, calibration heuristics, and ReAct loops were designed, verified, and tested by the team.


```
Author: 
- Tran Thien An - 24110077
- Le Ngoc Hai - 24110089
- Tran Gia Kiet - 24110103
This project is a part of subject in University, 2026 - 2027. This aims to build a RAG system to answer questions about Ho Chi Minh University of Technology and Engineering.
```