from fastapi import APIRouter, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.schemas import QueryRequest, ConversationNameRequest
from app.utils.database import db
from app.utils.helpers import get_table_details, validate_table_access
from app.config import settings
import os

router = APIRouter()

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    temperature=0
)

table_details_context = get_table_details()

@router.post("/query")
async def generate_sql_response(query_request: QueryRequest):
    try:
        question = query_request.user_prompt
        role = query_request.role
        
        # Check if question is DB related
        is_db_related = check_if_db_related(question)
        if not is_db_related:
            return handle_non_db_query(question)
            
        # Extract and validate table access
        tables = extract_tables(question)
        if not validate_table_access(role, tables):
            return handle_unauthorized_access(role)
            
        # Handle different query types
        if is_csv_request(question):
            return handle_csv_request(question, role, tables)
        elif is_chart_request(question):
            return handle_chart_request(question, role, tables)
            
        # Handle regular query
        return handle_regular_query(question, role, tables)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation-name")
async def generate_conversation_name(request: ConversationNameRequest):
    try:
        name = generate_name(request.user_prompt)
        return {"conversation_name": name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add implementation of helper functions mentioned above 