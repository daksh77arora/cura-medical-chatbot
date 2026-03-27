import pickle
import os
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_community.retrievers import BM25Retriever
from typing import List


class EnsembleRetrieverSimple(BaseRetriever):
    """Simple ensemble of dense + sparse retrievers using RRF fusion."""
    dense_retriever: object
    sparse_retriever: object = None
    dense_weight: float = 0.6
    sparse_weight: float = 0.4
    k: int = 5

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> List[Document]:
        dense_docs = self.dense_retriever.invoke(query)

        if self.sparse_retriever is None:
            return dense_docs[:self.k]

        sparse_docs = self.sparse_retriever.invoke(query)

        # Simple RRF fusion
        scores = {}
        for rank, doc in enumerate(dense_docs):
            key = doc.page_content[:100]
            scores[key] = scores.get(key, {"doc": doc, "score": 0})
            scores[key]["score"] += self.dense_weight * (1 / (rank + 1))
        for rank, doc in enumerate(sparse_docs):
            key = doc.page_content[:100]
            if key not in scores:
                scores[key] = {"doc": doc, "score": 0}
            scores[key]["score"] += self.sparse_weight * (1 / (rank + 1))

        ranked = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        return [item["doc"] for item in ranked[:self.k]]


def build_retriever(vectorstore):
    # Dense: semantic similarity retriever
    dense = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 8},
    )

    docs_path = "data/all_docs.pkl"
    if os.path.exists(docs_path):
        try:
            with open(docs_path, "rb") as f:
                all_docs = pickle.load(f)
            sparse = BM25Retriever.from_documents(all_docs)
            sparse.k = 8
            return EnsembleRetrieverSimple(
                dense_retriever=dense,
                sparse_retriever=sparse,
                k=5,
            )
        except Exception as e:
            print(f"Warning: BM25 setup failed ({e}), using dense-only retriever.")

    return dense
