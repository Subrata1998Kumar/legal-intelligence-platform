from sqlalchemy.orm import Session
from sqlalchemy import text
from .embedding_service import EmbeddingService
from ..models import Document, DocumentChunk, User
from ..auth import ROLE_HIERARCHY

class RetrievalService:
    @staticmethod
    async def search_relevant_chunks(
        db: Session, 
        query: str, 
        user: User, 
        limit: int = 5,
        is_table: bool = None,
        document_id: int = None
    ) -> list[dict]:
        # Generate embedding vector
        query_vector = await EmbeddingService.get_embedding(query)
        vector_str = "[" + ",".join(map(str, query_vector)) + "]"
        
        # Enforce Security Clearance (RBAC Metadata Filtering)
        user_clearance_level = ROLE_HIERARCHY.get(user.role, 1)
        clearance_list = [r for r, lvl in ROLE_HIERARCHY.items() if lvl <= user_clearance_level]
        clearance_placeholders = ", ".join(f"'{c}'" for c in clearance_list)

        # Dynamic where clauses for advanced metadata filtering
        query_conditions = [f"d.security_clearance IN ({clearance_placeholders})"]
        query_params = {"vector": vector_str, "limit": limit}
        
        if is_table is not None:
            query_conditions.append("dc.is_table = :is_table")
            query_params["is_table"] = is_table
            
        if document_id is not None:
            query_conditions.append("d.id = :document_id")
            query_params["document_id"] = document_id
            
        where_clause = " AND ".join(query_conditions)

        sql = text(f"""
            SELECT 
                dc.id, 
                dc.content, 
                dc.chunk_index, 
                dc.is_table,
                dc.table_json,
                d.filename, 
                d.security_clearance,
                1 - (dc.embedding <=> :vector) as similarity
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            WHERE {where_clause}
            ORDER BY dc.embedding <=> :vector
            LIMIT :limit
        """)
        
        results = db.execute(sql, query_params).fetchall()
        
        chunks = []
        for r in results:
            chunks.append({
                "id": r[0],
                "content": r[1],
                "chunk_index": r[2],
                "is_table": r[3],
                "table_json": r[4],
                "filename": r[5],
                "security_clearance": r[6],
                "similarity": float(r[7]) if r[7] is not None else 0.0
            })
        return chunks