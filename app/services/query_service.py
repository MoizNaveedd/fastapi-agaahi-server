from fastapi import APIRouter, HTTPException, Request
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from app.models.schemas import QueryRequest, ConversationNameRequest, DashboardRequest
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
import base64
import ast
from app.services.inline_graph_service import process_chart_request, plot_chart
from app.utils.dashboard_constant import get_chart_meta_info
from app.services.dashboard_service import set_graph_request
# from app.services.embedding_service import LocalKnowledgeBaseService
from app.models.schemas import KnowledgeBaseQuery
from app.services.context_service import ContextService


from app.utils.prompts import (
    QUERY_PROMPT,
    ANSWER_PROMPT,
    CONVERSATION_NAME_PROMPT,
    NON_DB_QUERY_PROMPT,
    DB_CHECK_PROMPT,
    TABLE_SELECTION_PROMPT,
    CSV_CHECK_PROMPT,
    CHART_CHECK_PROMPT,
    UNAUTHORIZED_ACCESS_PROMPT,
    QUERY_PROMPT_CSV
)

router = APIRouter()

# Update the database connection
# db = SQLDatabase.from_uri(settings.DATABASE_URL)

def get_llm(request: Request):
    """Get LLM instance from app state"""
    return request.app.state.llm

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

def handle_non_db_query(question: str, llm):
    """Handle queries that are not related to database operations"""
    casual_response = llm.invoke(NON_DB_QUERY_PROMPT.format(question=question)).content.strip()
    return {
        "response": clean_code_block(casual_response),
        "base64": None,
        "format": "html"
    }

def extract_selected_tables(question: str, llm) -> list:
    """Extract table names from the user question"""
    response = llm.invoke(TABLE_SELECTION_PROMPT.format(
        question=question,
        table_details=table_details_context
    )).content
    tables = [table.strip() for table in response.split(',')]
    print(tables)
    return tables

def handle_unauthorized_access(role: str, llm):
    """Handle case when user doesn't have access to requested tables"""
    response = llm.invoke(UNAUTHORIZED_ACCESS_PROMPT.format(role=role)).content.strip()
    return {
        "response": clean_code_block(response),
        "base64": None,
        "format": "html"
    }

def is_csv_request(question: str) -> bool:
    """Check if the request is for CSV output using keyword matching"""
    csv_keywords = ["csv", "report", "spreadsheet", "excel", "export", "download"]
    return any(keyword in question.lower() for keyword in csv_keywords)

def is_chart_request(question: str) -> bool:
    """Check if the request is for chart visualization"""
    graph_keywords = ["graph", "chart", "plot", "visualize", "visualization", "graphviz"]
    return any(keyword in question.lower() for keyword in graph_keywords)








# Below implementation for CSV request

def sanitize_query(response: dict) -> dict:
    query = response["query"]
    lowered = query.lower()

    # Strip OUTFILE, COPY TO, or anything similar
    if "into outfile" in lowered:
        query = query.split("INTO OUTFILE")[0].strip()
    elif "copy to" in lowered:
        query = query.split("COPY TO")[0].strip()

    response["query"] = query
    return response


# import re

def get_column_names_from_query(query: str) -> list:
    """
    Extract column names from a SQL query (robust to SELECT keyword variations and multiline).
    """
    # Use DOTALL so `.` matches newlines
    match = re.search(r"SELECT\s+(.*?)\s+FROM", query, re.IGNORECASE | re.DOTALL)
    if match:
        columns_str = match.group(1)
        # Split by commas not inside parentheses (handles functions like COUNT(...))
        columns = [col.strip() for col in re.split(r",\s*(?![^()]*\))", columns_str)]
        return columns
    return []


def full_sql_pipeline(inputs):
    # Inject schema into inputs
    inputs["schema"] = table_details_context

    try:
        # Step 1: Generate query using updated inputs
        uncleaned_query = generate_query_for_csv(inputs)
        query = clean_query(uncleaned_query)

        # Step 2: Sanitize query
        sanitized_response = sanitize_query({"query": query})  # expects a dict
        sanitized_query = sanitized_response["query"]

        # Step 3: Get column names from query (if applicable)
        column_names = get_column_names_from_query(sanitized_query)

        # Step 4: Execute query
        result = execute_sql(sanitized_query)
        if not result:
            raise ValueError("No results returned from query.")

        # Convert result to CSV format
        csv_data = convert_to_csv(column_names, result)

        return {
            "result": result,
            "query": sanitized_query,
            "csv_data": csv_data
        }

    except IndexError as e:
        # Log the error and provide more details about the issue
        print(f"IndexError: {str(e)} - Likely cause: empty or invalid table list.")
        raise HTTPException(status_code=500, detail="Error in extracting tables or generating query.")

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


def convert_to_csv(column_names, result):
    # Start by creating the header (first line) of the CSV
    csv_lines = [",".join(column_names)]  # This line contains column names, joined by commas
    result1 = ast.literal_eval(result)

    # Loop through the result rows and format each row into a CSV line
    for row in result1:
        if isinstance(row, dict):
            # If row is a dictionary, extract values in the same order as column names
            csv_lines.append(",".join([str(row.get(col, '')).replace("\n", " ").replace("\r", "") for col in column_names]))
        elif isinstance(row, (list, tuple)):
            # If row is a list/tuple, simply join values by commas
            csv_lines.append(",".join([str(val).replace("\n", " ").replace("\r", "") for val in row]))
        else:
            # If row is a single value, convert it to a string
            csv_lines.append(str(row))

    # Combine all lines into a single CSV string
    csv_data = "\n".join(csv_lines)

    # Convert CSV string to Base64
    csv_bytes = csv_data.encode('utf-8')
    csv_base64 = base64.b64encode(csv_bytes).decode('utf-8')
    # print(csv_base64)
    return csv_base64



def generate_csv_download_link(base64_csv: str, filename: str = "report.csv") -> str:
    return (
        f"<a href=\"data:text/csv;base64,{base64_csv}\" "
        f"download=\"{filename}\" "
        f"class='text-blue-600 underline ml-2'>Click here to download</a>"
    )

def generate_query_for_csv(input_data):
    llm = get_llm()
    return llm.invoke(QUERY_PROMPT_CSV.format(**input_data)).content.strip()
    # return llm.invoke(query_prompt.format(**input_data)).content.strip()


def handle_csv_request(question: str, role: str, tables: list, llm):
    """Handle request for CSV output"""
    try:

        chain = RunnableLambda(full_sql_pipeline)


        response = chain.invoke({
            "question": question,
            "role": role,
            "table_names_to_use": tables
        })

        if isinstance(response.get("result"), str) and "Error" in response["result"]:
            return {
                "response": "<div className='p-4 text-red-600'>Sorry, I couldn't generate a report.</div>",
                "base64": None,
                "format": "csv"
            }

        # Get column names from the query
        query = response["query"]
        column_names = get_column_names_from_query(query)
        
        # Convert result to CSV format
        csv_data = convert_to_csv(column_names, response["result"])
        html_link = generate_csv_download_link(csv_data)
        
        return {
            "response": (
                "<div className='bg-gray-100 py-4 px-6 rounded-3xl max-w-3xl ant-flex "
                "css-dev-only-do-not-override-tk01x6'>"
                "<span className='text-black'>Here is your generated report:</span>"
                f"{html_link}"
                "</div>"
            ),
            "base64": csv_data,
            "format": "csv"
        }

    except Exception as e:
        print(f"CSV generation error: {str(e)}")
        return {
            "response": "<div className='p-4 text-red-600'>Sorry, I couldn't generate a report.</div>",
            "base64": None,
            "format": "csv"
        }


# Bwlow implemenrarion is for chart request in chats

def handle_chart_request(question: str, role: str, tables: list, llm):
    """Handle request for chart visualization"""
    class DummyHistory:
        messages = [HumanMessage(content=question)]

    chart_info = process_chart_request(question, DummyHistory(), llm, db, "")
    if chart_info:
        base64_chart = plot_chart(chart_info, db)
        return {
            "response": "<div className='p-4 text-green-600'>Here is your chart:</div>",
            "base64": base64_chart,
            "format": "graph"
        }
    else:
        return {
            "response": "<div className='p-4 text-red-600'>Sorry, I couldn't create a chart from that.</div>",
            "base64": None,
            "format": "graph"
        }


def handle_regular_query(question: str, role: str, tables: list, llm):
    """Handle standard SQL query generation and execution"""
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

def check_if_db_related(input_data, llm):
    """Determine if a question is related to any database tables."""
    response = llm.invoke(DB_CHECK_PROMPT.format(**input_data)).content.strip().lower()
    return "yes" in response.lower() if response else False

def generate_name(conversation: str, llm) -> str:
    """Generate a name for the conversation"""
    return llm.invoke(CONVERSATION_NAME_PROMPT.format(user_prompt=conversation)).content.strip()


@router.post("/query")
async def generate_sql_response(query_request: QueryRequest, request: Request):
    try:
        llm = get_llm(request)
        question = query_request.user_prompt
        role = query_request.role
        
        # Check if question is DB related
        is_db_related = check_if_db_related({"question": question, "schema": table_details_context}, llm)
        if not is_db_related:
            return handle_non_db_query(question, llm)
            
        # Extract and validate table access
        tables = extract_selected_tables(question, llm)
        if not validate_table_access(role, tables):
            return handle_unauthorized_access(role, llm)
            
        # Handle different query types
        if is_csv_request(question):
            return handle_csv_request(question, role, tables, llm)
        elif is_chart_request(question):
            return handle_chart_request(question, role, tables, llm)
            
        # Handle regular query
        return handle_regular_query(question, role, tables, llm)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation-name")
async def generate_conversation_name(name_prompt: ConversationNameRequest,request: Request):
    try:
        llm = get_llm(request)
        name = generate_name(name_prompt.user_prompt, llm)
        return {"conversation_name": clean_code_block(name)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 

@router.post('/dashboard')
async def dashboard(request: DashboardRequest):
    try:
        return await set_graph_request(request, get_chart_meta_info())
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred. in dashboard")


# from .embedding_service import LocalKnowledgeBaseService

# Initialize knowledge base service once
# knowledge_base_service = LocalKnowledgeBaseService()

class QueryService:
    def __init__(self):
        self.context_service = ContextService()

    def get_llm_response(self, prompt: str, llm=None) -> dict:
        """Get response from LLM"""
        try:
            if not llm:
                return {
                    "response": """
                        <div className='p-4 bg-red-50 rounded-lg'>
                            <div className='text-red-700'>LLM not properly configured.</div>
                        </div>
                    """,
                    "format": "text"
                }

            response = llm.invoke(prompt).content.strip()

            return {
                "response": f"""
                    <div className='p-4 bg-blue-50 rounded-lg'>
                        <div className='text-gray-700'>{response}</div>
                    </div>
                """,
                "format": "text"
            }

        except Exception as e:
            print(f"LLM Error: {str(e)}")
            return {
                "response": """
                    <div className='p-4 bg-red-50 rounded-lg'>
                        <div className='text-red-700'>Error processing request.</div>
                    </div>
                """,
                "format": "text"
            }

    def _is_about_agaahi(self, query: str) -> bool:
        """Check if query is about Agaahi"""
        agaahi_keywords = [
            "agaahi", "what is agaahi", "tell me about agaahi",
            "who made", "who created", "founder", "developer",
            "how does agaahi", "features", "capabilities"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in agaahi_keywords)

    def process_query(self, query: str, llm=None) -> dict:
        """Process the incoming user query and prepare a prompt for the LLM"""
        try:
            if self._is_about_agaahi(query):
                # Get Agaahi-specific context
                relevant_contexts = self.context_service.get_relevant_context(query)
                context_text = "\n".join(relevant_contexts)

                prompt = f"""Context information about Agaahi:
{context_text}

User question: {query}

Please provide a response that:
1. Directly answers their question about Agaahi using the context
2. Highlights relevant features or information
3. Maintains a professional and friendly tone
4. Asks if they would like to know more about any specific aspect of Agaahi

If the context doesn't fully answer their question, focus on what is known from the context."""
            else:
                # For non-Agaahi queries
                prompt = f"""You are Agaahi, an AI assistant. The user has asked: {query}

                        Please provide a response that:
                        1. Politely explains that you are Agaahi, an AI database assistant when use say hi or hello or greeting message
                        2. Mentions that you specialize in helping with database queries and data analysis and also respond to the question user asked
                        3. Maintains a helpful and friendly tone
                        """

            return self.get_llm_response(prompt, llm)

        except Exception as e:
            print(f"Query Processing Error: {str(e)}")
            return {
                "response": """
                    <div className='p-4 bg-red-50 rounded-lg'>
                        <div className='text-red-700'>Error processing query.</div>
                    </div>
                """,
                "format": "text"
            }


# Initialize the QueryService
query_service = QueryService()

@router.post("/knowledge-base/query")
async def query_knowledge_base(query: KnowledgeBaseQuery, request: Request):
    try:
        llm = get_llm(request)
        response = query_service.process_query(query.question, llm)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing knowledge base query: {str(e)}"
        )
