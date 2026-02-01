# Justify Legal AI

RAG-based legal assistant for Bangladesh providing AI-powered answers to legal questions by retrieving and citing specific articles from the Constitution of Bangladesh.

**Stack:** FastAPI + LangChain + ChromaDB + Claude 3.5 Sonnet + OpenAI Embeddings

## Features

- 🔍 Semantic search across Bangladesh Constitution articles
- 🎯 Citation-backed responses with Article numbers and names
- 🌐 Bilingual support (English & Bengali)
- 📚 Part and Article metadata for comprehensive context
- 🚫 Strict grounding - refuses to answer without legal source

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- OpenAI API key (for embeddings)
- Anthropic API key (for Claude 3.5 Sonnet)

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/KayesAshfaQ/law_agent.git
cd law_agent
```

### 2. Install Dependencies

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
CHROMA_PATH=chroma_db
COLLECTION_NAME=justify_legal_docs
```

### 4. Ingest Legal Documents

Process the Constitution data and create the vector database:

```bash
uv run python app/engine/ingest.py
```

This will:
- Parse `data/bd_constitution.json`
- Generate embeddings using OpenAI's `text-embedding-3-small`
- Store vectors in ChromaDB at `chroma_db/`

## Usage

### Start the API Server

```bash
uv run uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`

### Test the API

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Ask a Legal Question:**
```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What does Article 27 say about equality?"}'
```

**Example Response:**
```json
{
  "answer": "According to **Article 27 - Equality before law** from **Part III - Fundamental Rights** of the Constitution:\n\n- All citizens are equal before law and are entitled to equal protection of law.\n\nThis article establishes the fundamental principle of legal equality in Bangladesh."
}
```

### Test RAG Chain Directly

```bash
uv run python -c "
from app.engine.rag_chain import build_rag_chain
chain = build_rag_chain()
response = chain.invoke('What are fundamental rights in Bangladesh?')
print(response)
"
```

## Project Structure

```
law_agent/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── engine/
│   │   ├── ingest.py          # Document ingestion pipeline
│   │   └── rag_chain.py       # RAG chain with LangChain
│   ├── api/
│   │   └── v1/endpoints/
│   │       └── chat.py        # Chat API endpoint
│   └── models/
│       └── chat_schemas.py    # Pydantic request/response models
├── data/
│   └── bd_constitution.json   # Constitution articles (English + Bengali)
├── chroma_db/                 # Vector database (auto-generated)
├── pyproject.toml             # Project dependencies
└── README.md
```

## How It Works

1. **Ingestion:** Constitution articles are parsed, embedded, and stored in ChromaDB
2. **Retrieval:** User query is embedded and top 4 relevant articles are retrieved
3. **Generation:** Claude 3.5 Sonnet generates a grounded response with citations
4. **Response:** Markdown-formatted answer with Article numbers and Part references

## Configuration

### Retrieval Settings

Adjust in [app/engine/rag_chain.py](app/engine/rag_chain.py):

```python
return vectorstore.as_retriever(search_kwargs={"k": 4})  # Change number of chunks
```

### Model Parameters

Modify Claude settings:

```python
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
    temperature=0,      # 0 for deterministic responses
    max_tokens=1024     # Adjust response length
)
```

## Re-ingesting Data

If you update `data/bd_constitution.json`:

```bash
uv run python app/engine/ingest.py
```

The script automatically clears the old database and rebuilds from scratch.

## Development

### Run with Auto-reload

```bash
uv run uvicorn app.main:app --reload --port 8000
```

### Add New Dependencies

```bash
uv add package-name
```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a PR.
