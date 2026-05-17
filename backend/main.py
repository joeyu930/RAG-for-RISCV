import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
# Replaced native chains with a robust SimpleRagChain implementation
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama

app = FastAPI(title="RISC-V Assistant API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global variables for our ML models
vectorstore = None
retriever = None
llm = None
rag_chain = None

DB_DIR = "chroma_db"

@app.on_event("startup")
async def startup_event():
    global vectorstore, retriever, llm, rag_chain
    print("Loading embedding model...")
    # Matches the model used in ingest.py
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    if os.path.exists(DB_DIR):
        print("Connecting to local Chroma DB...")
        vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embedding_model)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    else:
        print("WARNING: Chroma DB not found. Please run ingest.py first.")
        
    print("Connecting to local Ollama LLM...")
    # Ensure you have ollama installed and have pulled a model like llama3 or mistral
    # e.g., 'ollama run llama3'
    try:
        llm = Ollama(model="qwen2.5:7b")
        
        system_prompt = (
            "You are an expert hardware engineering assistant specializing in the RISC-V architecture. "
            "Use the following pieces of retrieved context from the official RISC-V specifications to answer the user's question. "
            "If you don't know the answer, just say that you don't know, don't try to make up an answer. "
            "Keep the answer concise and highly technical, focusing on hardware development details."
            "\n\nContext:\n{context}"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])
        
        if retriever:
            classify_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an AI router. Classify the user input as 'TECH' if it's about hardware, engineering, RISC-V, processors, instructions, or tech facts. Classify as 'CHAT' if it's a greeting, casual chat, or completely unrelated. Reply ONLY with the word TECH or CHAT."),
                ("human", "{input}")
            ])
            chat_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a friendly RISC-V hardware assistant. The user is just chatting or greeting you. Reply politely, do not invent technical facts. Keep it short."),
                ("human", "{input}")
            ])

            class SimpleRagChain:
                def invoke(self, inputs):
                    user_input = inputs["input"]
                    
                    # 1. Classify intent (Semantic Routing)
                    intent_val = classify_prompt.invoke({"input": user_input})
                    intent_result = llm.invoke(intent_val)
                    intent_str = intent_result.content.strip().upper() if hasattr(intent_result, "content") else str(intent_result).strip().upper()
                    
                    # 2. Route based on intent
                    if "CHAT" in intent_str:
                        chat_val = chat_prompt.invoke({"input": user_input})
                        chat_result = llm.invoke(chat_val)
                        answer_text = chat_result.content if hasattr(chat_result, "content") else str(chat_result)
                        return {"answer": answer_text, "context": []}  # empty context avoids showing pages!
                    
                    # 3. Standard Technical RAG Pipeline
                    docs = retriever.invoke(user_input)
                    context_str = "\n\n".join(doc.page_content for doc in docs)
                    prompt_val = prompt.invoke({"context": context_str, "input": user_input})
                    
                    result = llm.invoke(prompt_val)
                    answer_text = result.content if hasattr(result, "content") else str(result)
                    return {"answer": answer_text, "context": docs}
                    
            rag_chain = SimpleRagChain()
            
        print("Backend is fully initialized.")
    except Exception as e:
        print(f"Error initializing LLM (Make sure Ollama is running): {e}")

class QueryRequest(BaseModel):
    query: str

class SourceDetail(BaseModel):
    page_content: str
    metadata: dict

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceDetail]

@app.post("/api/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    if not rag_chain:
        raise HTTPException(status_code=500, detail="Backend not fully initialized. Check DB and Ollama.")
    
    try:
        response = rag_chain.invoke({"input": request.query})
        
        sources = []
        if "context" in response:
            for doc in response["context"]:
                sources.append({
                    "page_content": doc.page_content,
                    "metadata": doc.metadata
                })
                
        return QueryResponse(
            answer=response["answer"],
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
