from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest, ChatResponse, Source
from app.core.security import rate_limit, get_session
from app.services.safety import MedicalSafetyFilter
import structlog, json, uuid

router = APIRouter()
log = structlog.get_logger()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    body: ChatRequest,
    session_id: str = Depends(get_session),
    _: None = Depends(rate_limit),
):
    log.info("chat.request", session_id=session_id, length=len(body.message))

    # Safety check
    if MedicalSafetyFilter.is_emergency(body.message):
        return ChatResponse(
            answer="⚠️ This sounds like a medical emergency. Please call 112 or go to your nearest emergency room immediately.",
            sources=[],
            is_emergency=True,
            session_id=session_id
        )
        
    is_in_scope, out_of_scope_msg = MedicalSafetyFilter.check_scope(body.message)
    if not is_in_scope:
        return ChatResponse(
            answer=out_of_scope_msg,
            sources=[],
            session_id=session_id
        )

    try:
        if request.app.state.rag is None:
            from app.rag.pipeline import RAGPipeline
            request.app.state.rag = await RAGPipeline.create()
            
        rag = request.app.state.rag
        result = await rag.invoke(message=body.message, session_id=session_id)
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            session_id=session_id,
        )
    except Exception as e:
        log.error("chat.error", error=str(e), session_id=session_id)
        raise HTTPException(500, "Sorry, I encountered an error. Please try again.")

@router.post("/chat/stream")
async def chat_stream(request: Request, body: ChatRequest):
    async def event_stream():
        if request.app.state.rag is None:
            from app.rag.pipeline import RAGPipeline
            request.app.state.rag = await RAGPipeline.create()
        
        rag = request.app.state.rag
        
        # If not initialized, do it now with progress updates
        if rag.chain is None:
            async def report(msg):
                return f"data: {json.dumps({'token': f'\\n{msg}'})}\\n\\n"
            
            # Since we can't easily yield from inside initialize without a generator,
            # we'll just do it manually here for the first-time setup
            yield f"data: {json.dumps({'token': '🔄 Initializing MediBot Brain...' })}\n\n"
            
            # Step 1: Embeddings
            from src.helper import download_hugging_face_embeddings
            yield f"data: {json.dumps({'token': '\n📥 Loading AI Embeddings...' })}\n\n"
            rag.embeddings = download_hugging_face_embeddings()
            
            # Step 2: Vector Store
            yield f"data: {json.dumps({'token': '\n🔍 Connecting to Vector Store...' })}\n\n"
            from app.rag.pinecone_store import PineconeV8VectorStore
            from app.core.config import settings
            rag.vectorstore = PineconeV8VectorStore.from_existing_index(
                index_name=settings.PINECONE_INDEX,
                embedding=rag.embeddings,
                api_key=settings.PINECONE_API_KEY.get_secret_value(),
            )
            
            # Step 3: Chain
            yield f"data: {json.dumps({'token': '\n🤖 Ready! Generating answer...\n\n' })}\n\n"
            await rag.initialize() # Finishes the rest quietly
        
        async for chunk in rag.stream(body.message):
            yield f"data: {json.dumps({'token': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
