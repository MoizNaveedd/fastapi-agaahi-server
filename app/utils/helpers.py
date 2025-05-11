import pandas as pd
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import ast
# import seaborn as sns
import os
from app.config import settings

def get_table_details():
    sheet_url = "https://docs.google.com/spreadsheets/d/1jdEQre3MzvtM6bu71cN6WQs5-ILnojA1-qCNOF6XSHQ/export?format=csv"
    df = pd.read_csv(sheet_url)
    
    table_details = ""
    for index, row in df.iterrows():
        table_details += f"Table Name: {row['Table Name']}\nTable Description: {row['Table Description']}\nAttributes: {row['Attributes']}\n\n"
    return table_details

ROLE_TABLE_ACCESS = {
    "admin": ["orders", "customers", "payments", "products", "employees", "order_items"],
    "data_analyst": ["orders", "order_items", "customers", "products"],
    "data_engineer": ["products", "suppliers"],
    "owner": ["orders", "customers", "payments", "shipping", "employees", "order_items"]
}

def validate_table_access(role: str, tables: list) -> bool:
    allowed_tables = ROLE_TABLE_ACCESS.get(role, [])
    return all(table in allowed_tables for table in tables)

def validate_table_access_v2(allowed_tables: list, tables: list) -> bool:
    # allowed_tables = ROLE_TABLE_ACCESS.get(role, [])
    return all(table in allowed_tables for table in tables)

def save_chart(fig, chart_type: str, x_axis: str, y_axis: str) -> str:
    os.makedirs(settings.CHART_DIR, exist_ok=True)
    
    # Save to buffer for base64
    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close()
    buffer.seek(0)
    
    # Convert to base64
    img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    return img_base64 


def check_if_db_related(input_data):
    """Determine if a question is related to any database tables."""
    schema = input_data["schema"]
    question = input_data["question"]

    # Create a prompt to check if the question is DB-related
    db_check_prompt = f"""
    Given the following database schema and user question, determine if the question is related to database queries.

    Database Schema:
    {schema}

    User Question: {question}

    Answer with only "yes" or "no":
    - "yes" if the question is asking for data that would be found in the database tables
    - "no" if the question is casual conversation, greeting, or unrelated to database queries

    """

    # Get response from LLM
    response = llm.invoke(db_check_prompt).content.strip().lower()

    # Return True if the response contains "yes"
    return "yes" in response.lower() if response else False


# def extract_selected_tables(inputs):
#     question = inputs["question"]
#     print("in extraction", question)
#     tables = llm.invoke(system_message.format(
#         question=question,
#         table_details_context=table_details_context
#     )).content.strip()

#     try:
#         # Try to parse as a proper list
#         result = ast.literal_eval(tables)
#         if isinstance(result, list):
#             return result
#     except (ValueError, SyntaxError):
#         # If it's not a valid list, try to manually split and clean
#         result = [table.strip() for table in tables.split(",") if table.strip()]
#         return result



def extract_selected_tables(inputs, llm):

    table_details_context = get_table_details()

    system_message = """
    Extract all table names mentioned in the user's question.
    
    Example:
    Question: 'how many orders placed by customer John Doe'
    Answer: ['orders','customers']
    
    Instruction:
    - Do not write print statement and ``` just return simple string
    
    Question: {question}
    
    Database Schema: {table_details_context}
    """
    question = inputs["question"]
    print("in extraction", question)
    tables = llm.invoke(system_message.format(
        question=question,
        table_details_context=table_details_context
    )).content.strip()

    # Remove any common characters that might interfere with parsing
    tables = tables.replace('[', '').replace(']', '').replace('"', '').replace("'", '')
    
    # Split by comma and clean up each table name
    result = [table.strip().lower() for table in tables.split(',') if table.strip()]
    
    return result


def get_relevant_table_details(df, extracted_tables: list) -> str:
    """
    Returns table details only for the extracted tables.

    Args:
        df: The dataframe containing all table info from the Google Sheet.
        extracted_tables: List of table names that are relevant to the current question.

    Returns:
        A string containing details of only the relevant tables.
    """
    relevant_details = ""

    for index, row in df.iterrows():
        if row['Table Name'] in extracted_tables:
            relevant_details += (
                f"Table Name: {row['Table Name']}\n"
                f"Table Description: {row['Table Description']}\n"
                f"Attributes: {row['Attributes']}\n\n"
            )

    return relevant_details
