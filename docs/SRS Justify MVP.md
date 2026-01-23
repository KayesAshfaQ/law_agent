# **Software Requirements Specification (SRS)**

## **Project Name: Justify (MVP \- Bangladesh Region)**

**Version:** 1.0

**Status:** Draft

**Target Region:** Bangladesh

## **1\. Introduction**

### **1.1 Purpose**

The purpose of "Justify" is to democratize access to legal information for general citizens in Bangladesh. It is a Retrieval-Augmented Generation (RAG) AI assistant that answers questions regarding Constitutional Rights and fundamental laws, strictly grounded in verified statutes and case law.

### **1.2 Scope**

The MVP will focus on:

* **Region:** Bangladesh.  
* **Domain:** Constitutional Law, Fundamental Rights, and Arrest/Detention procedures.  
* **User Base:** General citizens (non-lawyers) seeking legal clarity.  
* **Core Function:** An AI chat interface that retrieves specific legal articles to answer user queries with citations.

## **2\. User Personas**

### **2.1 The Confused Citizen**

* **Scenario:** Has been stopped by traffic police or is facing a property dispute.  
* **Goal:** Wants to know, "Is this legal?" and "What are my rights?" in simple language.  
* **Pain Point:** Cannot understand complex legal PDFs; existing lawyers are too expensive for quick questions.

### **2.2 The Law Student (Secondary)**

* **Scenario:** Studying for exams or researching a topic.  
* **Goal:** Quickly find the specific Article or Act number related to a topic.

## **3\. Functional Requirements**

### **3.1 The "Justify" Engine (RAG System)**

* **FR-01: Ingestion:** The system must ingest and index the **Constitution of Bangladesh** and selected **Key Acts** (from the 2025 Kaggle Dataset) into a Vector Database.  
* **FR-02: Retrieval:** Upon receiving a user query, the system must search the Vector Database to find the top 3-5 most relevant legal segments.  
* **FR-03: Grounded Generation:** The AI must generate an answer using *only* the retrieved context.  
* **FR-04: Citation:** Every response must include a specific reference (e.g., *"Source: Article 36, Constitution of Bangladesh"*).  
* **FR-05: Hallucination Guard:** If the retrieved documents do not contain the answer, the AI must reply: *"I cannot find a specific law regarding this in my database."*

### **3.2 User Interface (UI)**

* **FR-06: Jurisdiction Selector:** A dropdown menu (defaulted to 'Bangladesh') to allow future global expansion.  
* **FR-07: Query Input:** A chat interface accepting natural language input (e.g., *"Can police arrest me without a warrant?"*).  
* **FR-08: "Simplify" Mode:** A toggle or request option to "Explain this like I'm 12."  
* **FR-09: Disclaimer Display:** A permanent footer or modal stating: *"Justify provides legal information, not legal advice. Consult a lawyer for professional representation."*

### **3.3 Language Support**

* **FR-10: Multilingual Understanding:** The system must accept queries in **Bengali** (typed or phonetic) and **English**.  
* **FR-11: Output Language:** The system should reply in the same language the user asked the question in.

## **4\. Non-Functional Requirements**

### **4.1 Accuracy & Safety**

* **NFR-01:** The system must strictly prioritize precision. It is better to refuse to answer than to answer incorrectly.  
* **NFR-02:** The system must not generate text that encourages illegal acts.

### **4.2 Performance**

* **NFR-03:** Response time should be under 5 seconds for a complete answer.

### **4.3 Data Privacy**

* **NFR-04:** User queries must be encrypted in transit. (If anonymous, no PII is stored).

## **5\. Technical Stack (Proposed)**

* **Frontend:** React.js or Streamlit (Python) for rapid MVP.  
* **Backend API:** FastAPI (Python).  
* **LLM Orchestration:** LangChain.  
* **LLM Model:** Claude 3.5 Sonnet (via API) or Gemini 1.5 Pro.  
* **Vector Database:** ChromaDB.  
* **Hosting:** Vercel (Frontend) / Railway or AWS (Backend).

## **6\. MVP Roadmap**

1. **Phase 1: Data Pipeline:** Clean Kaggle JSON → Embedding → Vector Store.  
2. **Phase 2: Core Logic:** Build the Python RAG function (Retrieve \+ Generate).  
3. **Phase 3: UI Build:** specific chat interface.  
4. **Phase 4: Testing:** Red-teaming (trying to make the AI lie) using legal experts.