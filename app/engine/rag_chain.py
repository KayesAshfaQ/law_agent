import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH", "chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "justify_legal_docs")

def get_retriever():
    """Loads the existing Chroma DB from disk."""
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    
    # Search configuration: Fetch top 4 most relevant chunks
    return vectorstore.as_retriever(search_kwargs={"k": 4})

def format_docs(docs):
    """Formats retrieved law chunks into a single string for the prompt."""
    formatted_chunks = []
    for doc in docs:
        source = doc.metadata.get('source', 'Unknown Act')
        section = doc.metadata.get('section', 'Unknown Section')
        formatted_chunks.append(f"SOURCE: {source} ({section})\nTEXT: {doc.page_content}")
    
    return "\n\n---\n\n".join(formatted_chunks)

def build_rag_chain():
    retriever = get_retriever()
    
    # Using Claude 3.5 Sonnet for high reasoning capability
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20240620", 
        temperature=0,
        max_tokens=1024
    )

    system_prompt = """You are 'Justify', a legal AI assistant for Bangladesh.
    
    Use the following pieces of retrieved legal context to answer the user's question.
    
    GUIDELINES:
    1. STRICTLY base your answer on the provided context. Do not use outside knowledge.
    2. If the answer is not in the context, say: "I cannot find a specific law in my database regarding this."
    3. CITE YOUR SOURCES. Mention the Act Name and Section Number for every claim.
    4. Format your answer in Markdown. Use bullet points for clarity.
    5. Be concise but accurate.

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