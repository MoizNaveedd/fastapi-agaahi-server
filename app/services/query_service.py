from fastapi import APIRouter, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from app.models.schemas import QueryRequest, ConversationNameRequest
from app.utils.database import db
from app.utils.helpers import get_table_details, validate_table_access
from app.config import settings
import os
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from operator import itemgetter
import re
from app.utils.prompts import (
    QUERY_PROMPT,
    ANSWER_PROMPT,
    CONVERSATION_NAME_PROMPT,
    NON_DB_QUERY_PROMPT,
    DB_CHECK_PROMPT,
    TABLE_SELECTION_PROMPT,
    CSV_CHECK_PROMPT,
    CHART_CHECK_PROMPT,
    UNAUTHORIZED_ACCESS_PROMPT
)

router = APIRouter()

# Update the database connection
# db = SQLDatabase.from_uri(settings.DATABASE_URL)

# Update get_llm function
def get_llm():
    """Initialize and return LLM instance"""
    return ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash-8b",
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY,
    )

# Add helper functions
def clean_query(raw_query: str) -> str:
    return re.sub(r"```sql|```", "", raw_query, flags=re.IGNORECASE).strip()

def execute_sql(query):
    execute_query = QuerySQLDataBaseTool(db=db)
    try:
        return execute_query.invoke(query)
    except Exception as sql_error:
        return f"Error executing SQL: {str(sql_error)}"

table_details_context = get_table_details()

def clean_code_block(code: str) -> str:
    # Remove ```jsx, ```html, or just ``` from the start, and ``` from the end
    return re.sub(r'^```(?:jsx|html)?\n|\n```$', '', code.strip())

def handle_non_db_query(question: str):
    """Handle queries that are not related to database operations"""
    llm = get_llm()
    casual_response = llm.invoke(NON_DB_QUERY_PROMPT.format(question=question)).content.strip()
    return {
        "response": clean_code_block(casual_response),
        "base64": None,
        "format": "html"
    }

def extract_selected_tables(question: str) -> list:
    """Extract table names from the user question"""
    llm = get_llm()
    response = llm.invoke(TABLE_SELECTION_PROMPT.format(
        question=question,
        table_details=table_details_context
    )).content
    tables = [table.strip() for table in response.split(',')]
    print(tables)
    return tables

def handle_unauthorized_access(role: str):
    """Handle case when user doesn't have access to requested tables"""
    llm = get_llm() 
    response = llm.invoke(UNAUTHORIZED_ACCESS_PROMPT.format(role=role)).content.strip()
    return {
        "response": clean_code_block(response),
        "base64": None,
        "format": "html"
    }

def is_csv_request(question: str) -> bool:
    """Check if the request is for CSV output"""
    llm = get_llm()
    response = llm.invoke(CSV_CHECK_PROMPT.format(question=question)).content
    return response.lower().strip() == "yes"

def is_chart_request(question: str) -> bool:
    """Check if the request is for chart visualization"""
    llm = get_llm()
    response = llm.invoke(CHART_CHECK_PROMPT.format(question=question)).content
    return response.lower().strip() == "yes"

def handle_csv_request(question: str, role: str, tables: list):
    """Handle request for CSV output"""
    # Implementation for CSV handling
    return {"message": "CSV generation not implemented yet"}

def handle_chart_request(question: str, role: str, tables: list):
    """Handle request for chart visualization"""
    # Implementation for chart handling
    return {"message": "Chart generation not implemented yet"}

def handle_regular_query(question: str, role: str, tables: list):
    """Handle standard SQL query generation and execution"""
    llm = get_llm()
    chain = (
        RunnablePassthrough()
        .assign(schema=lambda _: table_details_context)
        .assign(query=lambda x: llm.invoke(QUERY_PROMPT.format(**x)).content.strip())
        .assign(uncleaned_result=itemgetter("query") | RunnableLambda(clean_query))
        .assign(result=itemgetter("uncleaned_result") | RunnableLambda(execute_sql))
        .assign(final=lambda x: llm.invoke(ANSWER_PROMPT.format(**x)).content.strip())
    )


    response = chain.invoke({
        "question": question,
        "role": role,
        "table_names_to_use": tables
    })

    return {
        "response": clean_code_block(response["final"]),
        "format": "html"
    }

def check_if_db_related(input_data):
    """Determine if a question is related to any database tables."""
    llm = get_llm()
    response = llm.invoke(DB_CHECK_PROMPT.format(**input_data)).content.strip().lower()
    return "yes" in response.lower() if response else False

def generate_name(conversation: str) -> str:
    """Generate a name for the conversation"""
    llm = get_llm()
    return llm.invoke(CONVERSATION_NAME_PROMPT.format(user_prompt=conversation)).content.strip()

@router.post("/query")
async def generate_sql_response(query_request: QueryRequest):
    try:
        question = query_request.user_prompt
        role = query_request.role
        
        # Check if question is DB related
        is_db_related = check_if_db_related({"question": question, "schema": table_details_context})
        if not is_db_related:
            return handle_non_db_query(question)
            
        # Extract and validate table access
        tables = extract_selected_tables(question)
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
        return {"conversation_name": clean_code_block(name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 