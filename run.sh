#!/bin/bash

# Ensure Ollama is running in the background for local LLM
echo "Checking if Ollama is running (it is required for local LLM inference)..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Warning: Cannot connect to Ollama at http://localhost:11434."
    echo "Make sure Ollama is installed and running, e.g., 'ollama serve' and 'ollama run qwen2.5:7b'."
fi

echo "Starting Backend FastAPI server..."
cd backend
conda run --no-capture-output -n riscv_rag python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Starting Frontend Vite server..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "node_modules not found, running npm install..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!

echo "=========================================================="
echo "RISC-V RAG Assistant is running!"
echo "- Backend API: http://localhost:8000"
echo "- Frontend UI: Check Vite output above (usually http://localhost:5173)"
echo "Press Ctrl+C to stop."
echo "=========================================================="

trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM
wait
