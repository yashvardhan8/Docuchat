# DocuChat Backend

FastAPI service implementing the RAG pipeline. See the root `README.md` for full architecture, setup, and API documentation.

Quick start:

```bash
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env       # then add your GROQ_API_KEY
uvicorn app.main:app --reload
```

Run the evaluation script (after uploading documents referenced in `questions.json`):

```bash
python evaluate_rag.py
```
