from dotenv import load_dotenv
import os
import pickle
from src.helper import load_pdf_file, filter_to_minimal_docs, text_split, download_hugging_face_embeddings
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Load and process documents
print("Loading PDF files...")
extracted_data = load_pdf_file(data='data/')
filter_data = filter_to_minimal_docs(extracted_data)
print(f"Loaded {len(filter_data)} documents.")

# Save processed documents for BM25 retriever (hybrid search)
os.makedirs("data", exist_ok=True)
with open("data/all_docs.pkl", "wb") as f:
    pickle.dump(filter_data, f)
print(f"Saved {len(filter_data)} docs to data/all_docs.pkl")

text_chunks = text_split(filter_data)
print(f"Created {len(text_chunks)} text chunks.")

embeddings = download_hugging_face_embeddings()

pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "medical-chatbot"

if not pc.has_index(index_name):
    print(f"Creating Pinecone index '{index_name}'...")
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    print("Index created.")

index = pc.Index(index_name)

# Upsert vectors directly using Pinecone SDK v8
print(f"Embedding and upserting {len(text_chunks)} chunks...")
batch_size = 100
texts = [doc.page_content for doc in text_chunks]
vectors = embeddings.embed_documents(texts)

for i in range(0, len(text_chunks), batch_size):
    batch_chunks = text_chunks[i:i + batch_size]
    batch_vectors = vectors[i:i + batch_size]
    upsert_data = []
    for j, (doc, vec) in enumerate(zip(batch_chunks, batch_vectors)):
        upsert_data.append({
            "id": f"doc_{i+j}",
            "values": vec,
            "metadata": {**doc.metadata, "text": doc.page_content[:512]},
        })
    index.upsert(vectors=upsert_data)
    print(f"Upserted {min(i+batch_size, len(text_chunks))}/{len(text_chunks)} chunks")

print("\nDone! Vector store is ready. You can now run the FastAPI server.")