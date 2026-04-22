# RISC-V Hardware Assistant

<div align="center">
  <img width="776" height="616" alt="RISCV-RAG" src="https://github.com/user-attachments/assets/bde7923d-0a93-445c-8879-1cc4d8398027" />
</div>


A robust, offline-capable Retrieval-Augmented Generation (RAG) assistant tailored for RISC-V hardware development. Uses the official RISC-V standard manuals (Unprivileged ISA Specification) to answer technical queries accurately, backing up every statement with its exact source.

## ✨ Features

- **Automated Specification Retrieval**: Plucks the latest standard unprivileged instruction manuals directly from the [RISC-V GitHub Releases](https://github.com/riscv/riscv-isa-manual/releases/).
- **100% Local RAG Pipeline**: Data never leaves your machine. Designed natively for developers using local models.
  - **Vector Database**: Hosted on an embedded ChromaDB.
  - **Embeddings**: Utilizes the HuggingFace `all-MiniLM-L6-v2` local model natively.
  - **LLM Engine**: Hooks up directly to your machine's `Ollama` daemon (defaulting to the highly capable `qwen3.5:27b` model).
- **FastAPI Backend**: Rapid, type-safe Python API endpoints processing Langchain's Retrieval chains.
- **Glassmorphism UI**: High-end front-end dashboard powered by Vite, Vanilla JavaScript, and beautiful deep-layered CSS variables.

## 🛠 Prerequisites

1. **Conda**: Required for fetching project dependencies cleanly.
   ```bash
   conda create -n riscv_rag python=3.10
   ```
2. **Ollama**: Ensure you have [Ollama](https://ollama.com/) running locally. Wait for initialization and ensure you hold the qwen model:
   ```bash
   ollama pull qwen3.5:27b
   ```

## 🚀 Quick Start

1. **Environment Installation**:
   Before the first run, install Python dependencies and generate the initial Database!
   ```bash
   conda activate riscv_rag
   pip install -r requirements.txt

   # Download PDF & Embed local Vector Database (Takes roughly 1-2 mins on first run)
   python backend/ingest.py 
   ```

2. **Run Application**:
   Navigate back to the project root, simply execute the startup shell script. It will boot both the backend FastAPI server & the frontend UI simultaneously.
   ```bash
   bash run.sh
   ```
3. Look at your terminal and open the Vite port address (ex. `http://localhost:5173/`). Enjoy!

## 💡 Architecture Detail
- **Frontend** - Simple `<div id="app">` injected by `main.js`. Converts markdown streams into readable answers and highlights Vector source metadata tags indicating exact RISC-V document source pages.
- **Backend /ingest.py** - Loads `PyPDFLoader` -> `RecursiveCharacterTextSplitter` -> HuggingFace `sentence-transformers` -> `ChromaDB`.
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
