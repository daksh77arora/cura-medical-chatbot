import os
import json
import hashlib
import pickle
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain.document_loaders import PyPDFLoader

# Fix path resolution for local execution
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.helper import download_hugging_face_embeddings, filter_to_minimal_docs
from ingestion.chunking import smart_chunk

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')

TRACKER_FILE = "data/indexed_files.json"

def already_indexed(doc_hash):
    if not os.path.exists(TRACKER_FILE):
        return False
    with open(TRACKER_FILE, "r") as f:
        data = json.load(f)
    return doc_hash in data

def mark_indexed(doc_hash, filename):
    data = {}
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r") as f:
            data = json.load(f)
    data[doc_hash] = filename
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=4)

def ingest_directory(data_dir: str):
    embeddings = download_hugging_face_embeddings()
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index_name = "medical-chatbot"

    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    all_raw_docs = []
    
    for pdf_path in Path(data_dir).glob("**/*.pdf"):
        doc_hash = hashlib.md5(pdf_path.read_bytes()).hexdigest()
        
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        docs = filter_to_minimal_docs(docs)
        all_raw_docs.extend(docs)
        
        if already_indexed(doc_hash):
            print(f"Skipping already indexed file: {pdf_path.name}")
            continue
            
        print(f"Indexing new file: {pdf_path.name}")
        chunks = smart_chunk(docs, embeddings_model=embeddings)
        
        for doc in chunks:
            doc.metadata.update({
                "filename": pdf_path.name,
                "doc_hash": doc_hash,
                "category": "Medical Reference",
            })
            
        vectorstore.add_documents(chunks)
        mark_indexed(doc_hash, pdf_path.name)
        
    # Write sparse BM25 cache
    os.makedirs("data", exist_ok=True)
    with open("data/all_docs.pkl", "wb") as f:
        pickle.dump(all_raw_docs, f)

if __name__ == "__main__":
    ingest_directory("data/")
