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

    # Safety check before hitting the LLM
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
        rag = request.app.state.rag
        result = await rag.invoke(
            message=body.message,
            session_id=session_id,
        )
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
        async for chunk in request.app.state.rag.stream(body.message):
            yield f"data: {json.dumps({'token': chunk})}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
