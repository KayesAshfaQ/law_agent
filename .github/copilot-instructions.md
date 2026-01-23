# Copilot Instructions: Justify Legal AI

## Project Overview
RAG-based legal assistant for Bangladesh providing AI-powered answers to legal questions by retrieving and citing specific laws from a local ChromaDB vector database.

**Stack:** FastAPI + LangChain + ChromaDB + Claude 3.5 Sonnet + OpenAI Embeddings

## Architecture

### Core Components
1. **FastAPI Server** ([app/main.py](../app/main.py)): Entry point with CORS enabled for frontend integration
2. **RAG Chain** ([app/engine/rag_chain.py](../app/engine/rag_chain.py)): LangChain pipeline handling retrieval → Claude generation → response
3. **Ingestion Pipeline** ([app/engine/ingest.py](../app/engine/ingest.py)): One-time script to load `data/bangladesh_acts.json` → embeddings → ChromaDB
4. **API Endpoint** ([app/api/v1/endpoints/chat.py](../app/api/v1/endpoints/chat.py)): `/api/v1/ask` POST endpoint with async handling

### Critical Design Decisions
- **Chain initialized at module level** in [chat.py](../app/api/v1/endpoints/chat.py#L8) to avoid reloading vector DB on every request
- **Strict grounding:** System prompt enforces "STRICTLY base your answer on provided context" - responses must cite sources or admit "cannot find in database"
- **Metadata tracking:** Every retrieved chunk includes `source` (Act name) and `section` for citation formatting

## Development Workflow

### Environment Setup
```bash
# Uses uv for dependency management (pyproject.toml)
uv venv
source .venv/bin/activate
uv pip install -e .
```

Required `.env` variables:
- `OPENAI_API_KEY` (for embeddings: text-embedding-3-small)
- `ANTHROPIC_API_KEY` (for Claude 3.5 Sonnet)
- `CHROMA_PATH` (default: `chroma_db`)
- `COLLECTION_NAME` (default: `justify_legal_docs`)

### Key Commands
```bash
# Ingest legal documents (run once or when data changes)
python app/engine/ingest.py

# Start development server
uvicorn app.main:app --reload

# Health check
curl http://localhost:8000/health
```

## Project-Specific Patterns

### Data Structure
Legal data in `data/bangladesh_acts.json` follows structure:
```json
[
  {
    "title": "Act Name",
    "sections": [
      {"section_title": "Section X", "content": "Legal text..."}
    ]
  }
]
```

### Retrieval Configuration
- Fetches **top 4 chunks** (`k=4`) per query
- Uses `RunnableParallel` to pass both context and question to prompt
- Custom `format_docs()` function creates formatted context with SOURCE/SECTION/TEXT structure

### Response Format
All responses follow Markdown formatting with:
- Bullet points for clarity
- Explicit source citations (Act Name + Section Number)
- Fallback message if no relevant law found

## Common Tasks

### Adding New Legal Documents
1. Update `data/bangladesh_acts.json` with new acts/sections
2. Run `python app/engine/ingest.py` (clears old DB via `shutil.rmtree`)
3. Restart API server to reload chain

### Modifying RAG Behavior
- **Retrieval tuning:** Adjust `search_kwargs={"k": 4}` in [rag_chain.py](../app/engine/rag_chain.py#L24)
- **Prompt engineering:** Edit `system_prompt` in [rag_chain.py](../app/engine/rag_chain.py#L48-L64)
- **Model parameters:** Change `temperature` (0 for deterministic) or `max_tokens` in Claude init

### API Schema
- Request: `{"query": "your question"}`
- Response: `{"answer": "markdown formatted response with citations"}`
- See [app/models/chat_schemas.py](../app/models/chat_schemas.py) for Pydantic models

## Important Constraints

1. **No hallucinations allowed:** System must refuse to answer if legal text not in vector DB
2. **Citation mandatory:** Every legal claim requires Act + Section reference
3. **Target audience:** Non-lawyers in Bangladesh - answers must be accessible
4. **MVP scope:** Focus on Constitutional Rights, Fundamental Rights, Arrest/Detention procedures (see [docs/SRS Justify MVP.md](../docs/SRS%20Justify%20MVP.md))

## Testing & Validation
- Red-team testing critical: Try queries designed to make AI generate incorrect legal advice
- Verify all responses include proper citations
- Test edge cases where legal context doesn't exist in DB
