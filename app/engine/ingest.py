import json
import os
import shutil
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = "data/bangladesh_acts.json"
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "justify_legal_docs")

def load_data():
    """Parses the specific Kaggle JSON structure."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data file not found at {DATA_PATH}")

    print(f"Loading data from {DATA_PATH}...")
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    documents = []
    
    # Logic for "Bangladesh Legal Acts" JSON structure
    # Adjust key names ('title', 'sections', etc.) based on the actual JSON file inspection
    for act in raw_data:
        act_title = act.get('title', 'Unknown Act')
        
        for section in act.get('sections', []):
            section_title = section.get('section_title', 'Unknown Section')
            content = section.get('content', '')

            if not content:
                continue

            # This text block is what the AI reads to learn the law
            page_content = f"Act: {act_title}\nSection: {section_title}\n\nLegal Text:\n{content}"
            
            metadata = {
                "source": act_title,
                "section": section_title,
                "type": "statute"
            }
            
            documents.append(Document(page_content=page_content, metadata=metadata))

    print(f"Prepared {len(documents)} documents for ingestion.")
    return documents

def ingest_to_chroma(docs):
    # Optional: Clear old DB to avoid duplicates during MVP testing
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH) 

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    print(f"Creating Chroma database at {CHROMA_PATH}...")
    
    # This automatically persists to disk in the folder specified
    Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH
    )
    print("Ingestion Complete! Database saved locally.")

if __name__ == "__main__":
    docs = load_data()
    ingest_to_chroma(docs)