import os
from langchain_chroma import Chroma
from langchain_nomic import NomicEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "justify_legal_docs")

def get_retriever():
    """Loads the existing Chroma DB from disk."""
    embeddings = NomicEmbeddings(model="nomic-embed-text-v1.5")
    
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    
    # Search configuration: Fetch top 4 most relevant chunks
    return vectorstore.as_retriever(search_kwargs={"k": 4})

def format_docs(docs):
    """Formats retrieved Constitution articles into a single string for the prompt."""
    formatted_chunks = []
    for doc in docs:
        source = doc.metadata.get('source', 'Unknown Law')
        section = doc.metadata.get('section', 'Unknown Article')
        article_name = doc.metadata.get('article_name', '')
        part = doc.metadata.get('part', '')
        
        # Build header with all available metadata
        header = f"SOURCE: {source}\n"
        if part:
            header += f"PART: {part}\n"
        header += f"ARTICLE: {section}"
        if article_name:
            header += f" - {article_name}"
        
        formatted_chunks.append(f"{header}\n\nTEXT:\n{doc.page_content}")
    
    return "\n\n---\n\n".join(formatted_chunks)

def build_rag_chain():
    retriever = get_retriever()
    
    # Using Groq's Llama 3.1 70B for fast and accurate reasoning
    llm = ChatGroq(
        model="llama-3.1-70b-versatile",
        temperature=0,
        max_tokens=1024
    )

    system_prompt = """You are 'Justify', a legal AI assistant for Bangladesh specializing in Constitutional law.
    
    Use the following pieces of retrieved legal context from the Constitution of Bangladesh to answer the user's question.
    
    GUIDELINES:
    1. STRICTLY base your answer on the provided context. Do not use outside knowledge.
    2. If the answer is not in the context, say: "I cannot find specific information in the Constitution regarding this."
    3. CITE YOUR SOURCES. Always mention the Article Number and name for every claim (e.g., "Article 27 - Equality before law").
    4. When relevant, mention which Part of the Constitution the article belongs to.
    5. Format your answer in Markdown. Use bullet points for clarity.
    6. Be concise but accurate. Use accessible language for non-lawyers.
    7. If both English and Bengali text are provided, prioritize English but acknowledge the Bengali version exists.

    CONTEXT:
    {context}

    USER QUESTION:
    {question}
    """
    
    prompt = ChatPromptTemplate.from_template(system_prompt)

    chain = (
        RunnableParallel({
            "context": retriever | format_docs, 
            "question": RunnablePassthrough()
        })
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain