from langchain_experimental.text_splitter import SemanticChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter

def smart_chunk(docs, embeddings_model):
    # Semantic chunking groups related sentences together
    semantic_splitter = SemanticChunker(
        embeddings_model,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=85,
    )
    chunks = semantic_splitter.split_documents(docs)

    # Fallback: ensure no chunk exceeds 1200 tokens
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,   # 15% overlap — proper industry standard
        separators=["\n\n", "\n", ". ", "? ", " "],
    )
    return char_splitter.split_documents(chunks)
