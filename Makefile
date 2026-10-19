.PHONY: setup demo eval test embed chunk help

help:
	@echo "=========================================================="
	@echo "AIPR FINAL PROJECT - SOCIAL WORK (CTXH) RAG AGENT"
	@echo "=========================================================="
	@echo "Available commands:"
	@echo "  make setup - Install dependencies and prepare directories"
	@echo "  make chunk - Split raw markdown documents into chunks (data/ctxh_chunks.json)"
	@echo "  make embed - Compute neural vector embeddings and save (data/ctxh_embeddings.json)"
	@echo "  make demo  - Run 3-layer ReAct Agent live demo (Retrieve -> Compute -> Action & Verify)"
	@echo "  make eval  - Run evaluation benchmark on 12 test queries and log metrics"
	@echo "  make test  - Run unit test suite (pytest tests/ -v)"

setup:
	uv pip install -r requirements.txt || pip install -r requirements.txt
	python -c "import sys; print('Python runtime verified:', sys.version)"
	python -c "from pathlib import Path; Path('data/db').mkdir(parents=True, exist_ok=True); Path('logs').mkdir(parents=True, exist_ok=True); Path('results').mkdir(parents=True, exist_ok=True)"

demo:
	python run_demo.py

eval:
	python run_evaluation.py

chunk:
	python src/data_preprocessing/build_dataset.py

embed:
	python src/retrieval/vector_store.py

test:
	python -m pytest tests/ -v
