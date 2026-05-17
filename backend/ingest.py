from pathlib import Path
import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
DB_DIR = BASE_DIR / "chroma_db"
REPO_API_URL = "https://api.github.com/repos/riscv/riscv-isa-manual/releases/latest"
PDF_NAME = "riscv-spec.pdf"
FILE_PATH = DOCS_DIR / PDF_NAME
REQUEST_TIMEOUT_SECONDS = 30

def download_latest_spec():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
        
    print(f"Fetching latest release info from {REPO_API_URL}...")
    try:
        response = requests.get(REPO_API_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
        
        download_url = None
        for asset in data.get("assets", []):
            if asset.get("name") == PDF_NAME:
                download_url = asset.get("browser_download_url")
                break
                
        if not download_url:
            print(f"Could not find {PDF_NAME} in the latest release.")
            return False
            
        print(f"Downloading {PDF_NAME} from {download_url}...")
        pdf_resp = requests.get(download_url, timeout=REQUEST_TIMEOUT_SECONDS)
        pdf_resp.raise_for_status()
        
        with FILE_PATH.open("wb") as f:
            f.write(pdf_resp.content)
            
        print(f"Successfully downloaded to {FILE_PATH}")
        return True
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return False

def ingest_documents():
    if not FILE_PATH.exists():
        success = download_latest_spec()
        if not success:
            print("Failed to procure the document. Aborting ingestion.")
            return

    print("Loading document...")
    loader = PyPDFLoader(str(FILE_PATH))
    documents = loader.load()
    print(f"Loaded {len(documents)} pages.")

    print("Splitting text into chunks...")
    # standard extension docs can be quite technical, chunk appropriately
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")

    print("Initializing embedding model (this may take a moment to download)...")
    # Using a fast, local embedding model
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print(f"Storing chunks in ChromaDB at {DB_DIR}...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=str(DB_DIR)
    )
    print("Ingestion complete and database persisted!")

if __name__ == "__main__":
    ingest_documents()
