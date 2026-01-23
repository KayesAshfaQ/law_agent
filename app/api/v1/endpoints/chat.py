from fastapi import APIRouter, HTTPException
from app.models.chat_schemas import ChatRequest, ChatResponse
from app.engine.rag_chain import build_rag_chain

router = APIRouter()

# Initialize chain at module level to avoid reloading DB on every request
rag_chain = build_rag_chain()

@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    try:
        # The chain handles embedding -> retrieval -> generation
        response_text = await rag_chain.ainvoke(request.query)
        return ChatResponse(answer=response_text)
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")