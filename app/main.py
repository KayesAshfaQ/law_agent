from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import chat

app = FastAPI(title="Justify API - Bangladesh MVP")

# Allow your Frontend to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok", "db": "ChromaDB Local"}