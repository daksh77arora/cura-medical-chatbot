from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core.config import settings
from src.prompt import system_prompt

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

def get_memory(session_id: str):
    return RedisChatMessageHistory(
        session_id=session_id,
        url=settings.REDIS_URL,
        ttl=settings.SESSION_TTL_SECONDS,
        key_prefix="medibot:session:",
    )

def build_chain_with_memory(rag_chain):
    return RunnableWithMessageHistory(
        rag_chain,
        get_session_history=get_memory,
        input_messages_key="input",
        history_messages_key="history",
        output_messages_key="answer",
    )
