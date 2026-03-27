"""
Custom Pinecone v8 vectorstore wrapper for LangChain.
Uses the Pinecone SDK directly since langchain_pinecone and
langchain_community.vectorstores.Pinecone both require older SDK versions.
"""
import os
from typing import List, Any, Optional
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_core.embeddings import Embeddings
from pinecone import Pinecone


class PineconeV8VectorStore(VectorStore):
    """Custom VectorStore that wraps Pinecone SDK v8."""

    def __init__(self, index_name: str, embedding: Embeddings, api_key: str, namespace: str = ""):
        self._embedding = embedding
        self._namespace = namespace
        pc = Pinecone(api_key=api_key)
        self._index = pc.Index(index_name)

    @classmethod
    def from_existing_index(cls, index_name: str, embedding: Embeddings, api_key: str) -> "PineconeV8VectorStore":
        return cls(index_name=index_name, embedding=embedding, api_key=api_key)

    @classmethod
    def from_documents(cls, documents: List[Document], embedding: Embeddings,
                       index_name: str, api_key: str, batch_size: int = 100) -> "PineconeV8VectorStore":
        store = cls(index_name=index_name, embedding=embedding, api_key=api_key)
        store.add_documents(documents, batch_size=batch_size)
        return store

    def add_documents(self, documents: List[Document], batch_size: int = 100, **kwargs) -> List[str]:
        texts = [doc.page_content for doc in documents]
        vectors = self._embedding.embed_documents(texts)

        ids = []
        vectors_to_upsert = []
        for i, (doc, vec) in enumerate(zip(documents, vectors)):
            doc_id = f"doc_{i}"
            ids.append(doc_id)
            vectors_to_upsert.append({
                "id": doc_id,
                "values": vec,
                "metadata": {**doc.metadata, "text": doc.page_content[:512]},
            })

        # Upsert in batches
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            self._index.upsert(vectors=batch, namespace=self._namespace)
            print(f"Upserted batch {i // batch_size + 1}/{(len(vectors_to_upsert) - 1) // batch_size + 1}")

        return ids

    def similarity_search(self, query: str, k: int = 4, **kwargs) -> List[Document]:
        query_vector = self._embedding.embed_query(query)
        results = self._index.query(
            vector=query_vector,
            top_k=k,
            include_metadata=True,
            namespace=self._namespace,
        )
        docs = []
        for match in results.get("matches", []):
            meta = match.get("metadata", {})
            text = meta.pop("text", "")
            docs.append(Document(page_content=text, metadata=meta))
        return docs

    def as_retriever(self, search_type: str = "similarity",
                     search_kwargs: Optional[dict] = None, **kwargs):
        from langchain_core.vectorstores import VectorStoreRetriever
        k = (search_kwargs or {}).get("k", 5)
        return VectorStoreRetriever(
            vectorstore=self,
            search_type="similarity",
            search_kwargs={"k": k},
        )

    # Required abstract method stubs
    def add_texts(self, texts, metadatas=None, **kwargs):
        docs = [Document(page_content=t, metadata=m or {}) for t, m in zip(texts, metadatas or [{}] * len(texts))]
        return self.add_documents(docs)

    @classmethod
    def from_texts(cls, texts, embedding, metadatas=None, **kwargs):
        raise NotImplementedError("Use from_documents instead.")
