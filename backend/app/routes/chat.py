import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, ChatSession, ChatMessage
from ..schemas import ChatQuery, ChatResponse, ChatSessionResponse, ChatMessageResponse
from ..auth import get_current_user
from ..services.retrieval_service import RetrievalService
from ..services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Enterprise Chat Memory"])

@router.post("/sessions", response_model=ChatSessionResponse)
def create_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session_id = str(uuid.uuid4())
    session = ChatSession(id=session_id, user_id=current_user.id, title="New Conversation")
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/sessions", response_model=list[ChatSessionResponse])
def get_user_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.updated_at.desc()).all()

@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
def get_session_messages(session_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()

@router.post("/sessions/{session_id}/query", response_model=ChatResponse)
async def ask_assistant(session_id: str, query: ChatQuery, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
        
    chunks = await RetrievalService.search_relevant_chunks(db, query.message, current_user, limit=4)
    
    context_str = ""
    sources_meta = []
    for c in chunks:
        context_str += f"\n[Doc: {c['filename']}, Index: {c['chunk_index']}]\n{c['content']}\n"
        sources_meta.append({
            "filename": c['filename'],
            "chunk_index": c['chunk_index'],
            "similarity": c['similarity'],
            "clearance": c['security_clearance']
        })
        
    chat_history = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    history_str = ""
    for msg in chat_history[-6:]:
        history_str += f"\n{msg.role.capitalize()}: {msg.content}"
        
    prompt = f"""
    You are a professional Legal Assistant for the Law Department. You must provide defensible advice based strictly on the provided Context.
    
    Grounding Context:
    {context_str}
    
    Chat History:
    {history_str}
    
    Current Question:
    {query.message}
    
    Instructions:
    1. Answer the current question accurately.
    2. Cite the source files (e.g. [Document_Name, Chunk_Index]) matching the context when you make any claim.
    3. If the answer cannot be determined from the context, explicitly state that the repository lacks direct references.
    """
    
    response_text = await ChatService.generate_response(prompt)
    
    user_msg = ChatMessage(session_id=session_id, role="user", content=query.message)
    assistant_msg = ChatMessage(session_id=session_id, role="assistant", content=response_text)
    db.add(user_msg)
    db.add(assistant_msg)
    
    if session.title == "New Conversation":
        session.title = query.message[:50] + "..."
        
    db.commit()
    
    return ChatResponse(response=response_text, sources=sources_meta)