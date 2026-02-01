import json
import os
import shutil
from langchain_core.documents import Document
from langchain_nomic import NomicEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = "data/bd_constitution.json"
CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "justify_legal_docs")

def load_data():
    """Parses the Bangladesh Constitution JSON structure with English and Bengali content."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data file not found at {DATA_PATH}")

    print(f"Loading data from {DATA_PATH}...")
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    documents = []
    
    # Each item in the array represents one article/section of the Constitution
    for article in raw_data:
        law_name = article.get('law_name_en', 'Unknown Law')
        part_info = f"{article.get('part_no_en', '')} - {article.get('part_name_en', '')}".strip(' -')
        article_name = article.get('article_name_en', 'Unknown Article')
        section_no = article.get('section_no_en', 'Unknown')
        
        # English content
        content_en = article.get('content', '')
        
        # Bengali content (optional for bilingual support)
        content_bn = article.get('article_bn', '')
        
        if not content_en:
            continue

        # Format: Article Number + Name, then content
        # Include both English and Bengali for comprehensive search
        page_content = f"Article {section_no}: {article_name}\n"
        page_content += f"Part: {part_info}\n\n"
        page_content += f"English:\n{content_en}\n\n"
        
        if content_bn:
            page_content += f"বাংলা:\n{content_bn}"
        
        metadata = {
            "source": law_name,
            "section": f"Article {section_no}",
            "article_name": article_name,
            "part": part_info,
            "type": "constitution"
        }
        
        documents.append(Document(page_content=page_content, metadata=metadata))

    print(f"Prepared {len(documents)} documents for ingestion.")
    return documents

def ingest_to_chroma(docs):
    # Optional: Clear old DB to avoid duplicates during MVP testing
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH) 

    embeddings = NomicEmbeddings(model="nomic-embed-text-v1.5")
    
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