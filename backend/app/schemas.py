""" Pydantic schemas for API validation """
from pydantic import BaseModel, Field
from typing import List

class UserRegister(BaseModel):
    username: str = Field(..., example="justice_officer_a")
    password: str = Field(..., example="SecureSecretPass123!")
    role: str = Field(..., example="Legal_Officer", description="Roles: Legal_Officer, Senior_Advisor, Admin")

class UserLogin(BaseModel):
    username: str = Field(..., example="justice_officer_a")
    password: str = Field(..., example="SecureSecretPass123!")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str

class Citation(BaseModel):
    source_document: str = Field(description="The file name of the authoritative legal document.")
    chunk_id: int = Field(description="The specific chunk/paragraph index.")
    exact_quote: str = Field(description="The exact text snippet retrieved and used for grounding.")

class ComplianceRisk(BaseModel):
    risk_level: str = Field(description="Severity of conflict or compliance risk (e.g., High, Medium, Low).")
    description: str = Field(description="Detailed explanation of the conflict or risk identified.")
    conflicting_source: str = Field(description="The statute or circular being violated or contradicted.")

class StructuredLegalOpinion(BaseModel):
    executive_summary: str = Field(description="A high-level overview of the legal guidance.")
    detailed_analysis: str = Field(description="The formal, defensible legal opinion.")
    citations: List[Citation] = Field(description="Authoritative sources proving the claims.")
    risks_detected: List[ComplianceRisk] = Field(description="Conflicts, compliance gaps, or regulatory risks.")
    confidence_score: float = Field(description="Factual consistency/faithfulness rating (e.g., using HHEM) from 0 to 1.")

class QueryRequest(BaseModel):
    session_id: str = Field(..., example="session_12345")
    query: str = Field(..., example="What is the mandatory final approval step for a project launch and its deadline?")
