.PHONY: setup demo eval test report help

help:
	@echo "AIPR FINAL PROJECT - SOCIAL WORK (CTXH) RAG AGENT"
	@echo "Lệnh có sẵn:"
	@echo "  make setup   - Cài đặt môi trường và kiểm tra dữ liệu"
	@echo "  make demo    - Chạy demo Agent ReAct 3 tầng (Tra cứu -> Tính toán -> Ghi & Verify)"
	@echo "  make eval    - Chạy benchmark đánh giá testset 12 câu và sinh log vào logs/"
	@echo "  make test    - Chạy unit tests hệ thống (RAG, MCP, DB)"
	@echo "  make report  - Sinh file báo cáo Word (report.docx) nộp bài môn học"

setup:
	uv pip install -r requirements.txt || pip install -r requirements.txt
	python -c "import sys; print('Môi trường Python hợp lệ:', sys.version)"
	python -c "from pathlib import Path; Path('data/db').mkdir(parents=True, exist_ok=True); Path('logs').mkdir(parents=True, exist_ok=True); Path('results').mkdir(parents=True, exist_ok=True)"

demo:
	python run_demo.py

eval:
	python run_evaluation.py

test:
	python -m pytest tests/ -v

report:
	python generate_report.py

