from langchain.prompts import PromptTemplate

# SQL Query Generation Prompt
QUERY_PROMPT = PromptTemplate.from_template(
    """
    You are a MySQL expert. Given an input question and the following database schema, generate a correct MySQL query.
    - Never use `SELECT *`, only select relevant columns.
    - Ensure all column names exist in the schema.
    - Use `CURDATE()` if "today" is mentioned.
    - Use proper joins when needed.
    - Return ONLY the SQL query text with no additional comments, explanation, or metadata.

    Database Schema:
    {schema}

    User Question: {question}
    SQLQuery:
    """
)

# Answer Generation Prompt
ANSWER_PROMPT = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, generate a response.
    You are a frontend engineer specializing in Tailwind CSS and ReactJS.

    Given the user's original question, the SQL query generated, and the resulting SQL data,
    create a user-facing response wrapped in HTML elements using Tailwind CSS classes.

    Follow these strict rules:
    - Use "className" attribute instead of "class".
    - Do NOT include any JavaScript logic (no map, reduce, loops, conditional rendering, etc.).
    - Make it visually appealing (use spacing, fonts, borders, or colors when appropriate).
    - DO NOT include any explanations outside of the JSX.
    - Wrap the final answer inside a <div> tag unless specified otherwise.
    - Do not write ``` and jsx just return simple string

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
)

# Conversation Name Generation Prompt
CONVERSATION_NAME_PROMPT = PromptTemplate.from_template(
    """You are a naming assistant.

Given a user's input or query, generate a short and meaningful conversation name related to the topic.
Rules:
- Keep it between 1 and 5 words only.
- Make it clear, catchy, and directly related to the user's input.
- Respond ONLY with the conversation name and nothing else.

User Prompt: {user_prompt}

Conversation Name:"""
)

# Non-DB Query Handling Prompt
NON_DB_QUERY_PROMPT = """
You are a helpful assistant for a data analytics system whose name is Agaahi. The user has asked a question that doesn't appear
to be related to any database queries. Please respond in a friendly, conversational manner.

Create a user-facing response wrapped in HTML elements using Tailwind CSS classes.
Follow these strict rules:
- Use "className" attribute instead of "class".
- Make it visually appealing (use spacing, fonts, borders, or colors when appropriate).
- Wrap the final answer inside a <div> tag.

User Question: {question}
"""

# DB-Related Check Prompt
DB_CHECK_PROMPT = """
Given the following database schema and user question, determine if the question is related to database queries.

Database Schema:
{schema}

User Question: {question}

Answer with only "yes" or "no":
- "yes" if the question is asking for data that would be found in the database tables
- "no" if the question is casual conversation, greeting, or unrelated to database queries
"""

# Table Selection Prompt
TABLE_SELECTION_PROMPT = """
Given this question: {question}
And these available tables: {table_details}
Return only the table names mentioned or needed to answer the question as a comma-separated list.
"""

# CSV Check Prompt
CSV_CHECK_PROMPT = "Does this question ask for CSV output? Answer only yes or no: {question}"

# Chart Check Prompt
CHART_CHECK_PROMPT = "Does this question ask for a chart or visualization? Answer only yes or no: {question}"

# Unauthorized Access Prompt
UNAUTHORIZED_ACCESS_PROMPT = """
The user with role '{role}' has attempted to access data they don't have permission for.
Generate a polite but firm message explaining they don't have access to the requested data.
The message should be professional and suggest contacting an administrator if they believe this is an error.
""" 