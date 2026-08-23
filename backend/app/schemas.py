from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_hash: str
    security_clearance: str
    uploaded_at: datetime
    class Config:
        from_attributes = True

class ChatMessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime
    class Config:
        from_attributes = True

class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    class Config:
        from_attributes = True

class ChatQuery(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]

class OpinionCreate(BaseModel):
    title: str
    draft_content: str

class OpinionResponse(BaseModel):
    id: int
    title: str
    draft_content: str
    compliance_report: Dict[str, Any]
    status: str
    created_by: Optional[int]
    reviewed_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    status: str