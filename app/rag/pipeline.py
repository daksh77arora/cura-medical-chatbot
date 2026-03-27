from typing import Dict, AsyncGenerator, List
from langchain_core.documents import Document
from app.core.config import settings

def _format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

class RAGPipeline:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        self.chat_model = None
        self.chain = None
        self.retrieval_chain = None

    async def initialize(self, progress_callback=None):
        if progress_callback: await progress_callback("📥 Downloading AI Embeddings (80MB)...")
        from src.helper import download_hugging_face_embeddings
        self.embeddings = download_hugging_face_embeddings()

        if progress_callback: await progress_callback("🔍 Connecting to Pinecone Vector Index...")
        from app.rag.pinecone_store import PineconeV8VectorStore
        self.vectorstore = PineconeV8VectorStore.from_existing_index(
            index_name=settings.PINECONE_INDEX,
            embedding=self.embeddings,
            api_key=settings.PINECONE_API_KEY.get_secret_value(),
        )

        from app.rag.retriever import build_retriever
        self.retriever = build_retriever(self.vectorstore)

        if progress_callback: await progress_callback("🤖 Initializing Cohere LLM...")
        from langchain_cohere import ChatCohere
        from src.prompt import system_prompt
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnableParallel, RunnablePassthrough

        self.chat_model = ChatCohere(
            model="command-r-plus-08-2024",
            cohere_api_key=settings.COHERE_API_KEY.get_secret_value() if settings.COHERE_API_KEY else "",
            streaming=True,
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt + "\n\nContext:\n{context}"),
            ("human", "{input}"),
        ])

        self.chain = (
            RunnableParallel(
                {"context": self.retriever | _format_docs, "input": RunnablePassthrough()}
            )
            | prompt
            | self.chat_model
            | StrOutputParser()
        )

        self.retrieval_chain = RunnableParallel(
            {"context": self.retriever, "input": RunnablePassthrough()}
        )
        
        if progress_callback: await progress_callback("✅ AI Ready! Generating answer...")

    @classmethod
    async def create(cls):
        instance = cls()
        return instance

    async def invoke(self, message: str, session_id: str) -> Dict:
        if not self.chain:
            await self.initialize()
            
        retrieval_result = await self.retrieval_chain.ainvoke(message)
        docs = retrieval_result["context"]
        answer = await self.chain.ainvoke(message)

        sources = []
        for doc in docs:
            src = doc.metadata.get("source", "Unknown Source")
            source_name = src.split('/')[-1] if '/' in src else src
            sources.append({
                "page": doc.metadata.get("page", 0),
                "content_preview": doc.page_content[:150],
                "source_file": source_name,
                "relevance_score": 0.0,
            })

        return {"answer": answer, "sources": sources}

    async def stream(self, message: str) -> AsyncGenerator[str, None]:
        if not self.chain:
            await self.initialize()
            
        async for chunk in self.chain.astream(message):
            if chunk:
                yield chunk

    async def cleanup(self):
        pass
