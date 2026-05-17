# RISC-V Hardware Assistant

<div align="center">
  <img width="776" height="616" alt="RISCV-RAG" src="https://github.com/user-attachments/assets/bde7923d-0a93-445c-8879-1cc4d8398027" />
</div>


A robust, local-first Retrieval-Augmented Generation (RAG) assistant tailored for RISC-V hardware development. Uses the official RISC-V standard manuals (Unprivileged ISA Specification) to answer technical queries accurately, backing up every statement with its exact source.

## ✨ Features

- **Automated Specification Retrieval**: Downloads the latest standard unprivileged instruction manual from the [RISC-V GitHub Releases](https://github.com/riscv/riscv-isa-manual/releases/) during ingestion.
- **Local RAG Pipeline**: After dependencies and the specification are downloaded, retrieval and generation run locally. Data does not leave your machine during normal chat usage.
  - **Vector Database**: Hosted on an embedded ChromaDB.
  - **Embeddings**: Utilizes the HuggingFace `all-MiniLM-L6-v2` local model natively.
  - **LLM Engine**: Hooks up directly to your machine's `Ollama` daemon (defaulting to the highly capable `qwen2.5:7b` model).
- **FastAPI Backend**: Rapid, type-safe Python API endpoints processing Langchain's Retrieval chains.
- **Glassmorphism UI**: Front-end dashboard powered by Vite, Vanilla JavaScript, local Markdown rendering, and deep-layered CSS variables.

## 🛠 Prerequisites

1. **Conda**: Required for fetching project dependencies cleanly.
   ```bash
   conda create -n riscv_rag python=3.10
   ```
2. **Ollama**: Ensure you have [Ollama](https://ollama.com/) running locally. Wait for initialization and ensure you hold the qwen model:
   ```bash
   ollama pull qwen2.5:7b
   ```

## 🚀 Quick Start

1. **Environment Installation**:
   Before the first run, install Python dependencies and generate the initial database.
   ```bash
   conda activate riscv_rag
   pip install -r requirements.txt

   # Download PDF and build backend/chroma_db (takes roughly 1-2 mins on first run)
   python backend/ingest.py 
   ```

   The ingestion script stores generated files under `backend/docs/` and `backend/chroma_db/` regardless of the directory you run it from.

2. **Frontend Dependencies**:
   Install the Vite dependencies once. `run.sh` also does this automatically if `frontend/node_modules` is missing.
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Run Application**:
   Navigate back to the project root, simply execute the startup shell script. It will boot both the backend FastAPI server & the frontend UI simultaneously.
   ```bash
   bash run.sh
   ```
4. Look at your terminal and open the Vite port address (ex. `http://localhost:5173/`). Enjoy!

The backend CORS configuration allows the default Vite origins: `http://localhost:5173` and `http://127.0.0.1:5173`.

## 💡 Architecture Detail

```
RAG-for-RISCV/
├── backend/
│   ├── docs/
│   │   └── riscv-spec.pdf          # auto-downloaded by ingest.py
│   ├── chroma_db/                  # auto-generated vector database
│   ├── ingest.py                   # PDF → chunks → embeddings → ChromaDB
│   └── main.py                     # FastAPI server with RAG + semantic routing
├── frontend/
│   ├── index.html                  # single-page app entry point
│   ├── main.js                     # chat UI logic & API client
│   ├── style.css                   # glassmorphism styles
│   └── package.json
├── requirements.txt
├── run.sh                          # starts backend + frontend concurrently
└── README.md
```

- **Frontend** - Simple `<div id="app">` driven by `main.js`. Converts Markdown into sanitized HTML and highlights vector source metadata tags indicating exact RISC-V document source pages.
- **Backend /ingest.py** - Downloads the PDF if needed, then loads `PyPDFLoader` -> `RecursiveCharacterTextSplitter` -> HuggingFace `sentence-transformers` -> `ChromaDB`.
- **Backend /main.py** - FastAPI standard `/api/chat` router equipped with **LLM Semantic Routing**. It dynamically evaluates incoming messages classifying them as `TECH` or `CHAT`:
  - `TECH`: Queries the VectorDB, fetches relevant contexts, and completes standard RAG augmented generation.
  - `CHAT`: Seamlessly bypasses RAG and engages in general conversation without rendering irrelevant reference pages.

## 🎯 Examples

1. **Base ISA Understanding**
   > *"What are the core differences between the RV32I and RV64I base integer instruction sets?"*

2. **Extensions & Features**
   > *"Describe the "Zicsr" extension for Control and Status Register instructions."*
   > *"What are the rounding modes defined in the floating-point extension (F and D extensions)?"*

3. **Memory & Synchronization Details**
   > *"What does the `fence.i` instruction do and when should a software developer use it?"*
   > *"How does the RISC-V hardware handle unaligned memory accesses according to the standard?"*
