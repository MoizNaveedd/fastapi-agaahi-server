from langchain.prompts import PromptTemplate

# SQL Query Generation Prompt
QUERY_PROMPT = PromptTemplate.from_template(
    """
    You are a MySQL expert. Given an input question and the following database schema, generate a correct MySQL query.
    - Do not use `SELECT *`, only select relevant columns.
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

QUERY_PROMPT_FOR_EDITOR= PromptTemplate.from_template(
       """
    You are a MySQL expert. Given an input question and the following database schema, generate a correct MySQL query.
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

QUERY_PROMPT_CSV = PromptTemplate.from_template(
    """
    You are a strict MySQL expert. Never use `SELECT *` under any condition. 
    Always specify relevant column names based on the given schema. 
    Never assume. If a user request is ambiguous, respond with a clarifying SQL query using only available schema details. 
    Only output valid SQL.

    Given an input question and the following database schema, generate a correct MySQL query.
    - Do not use `SELECT *`, only select relevant columns.
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
    """Given the following user question, corresponding SQL result, and analysis, generate a response.
You are a frontend engineer specializing in Tailwind CSS and ReactJS.

Create a STATIC user-facing response wrapped in HTML elements using Tailwind CSS classes.

STRICT RULES - VIOLATIONS ARE NOT ALLOWED:
1. ABSOLUTELY NO JAVASCRIPT:
   - NO map(), forEach, or any loops
   - NO array methods
   - NO conditional statements or ternary operators
   - NO variables or constants
   - NO functions or event handlers
   - NO dynamic content or templating

2. HTML/CSS ONLY:
   - Use "className" attribute instead of "class"
   - Use only static HTML elements (<div>, <p>, <table>, etc.)
   - Use Tailwind CSS classes for styling
   - All data must be directly written out, not programmatically generated

3. FORMAT:
   - Wrap everything in a single <div> tag
   - The top-level <div> must include the following Tailwind CSS classes to enable light and dark mode:
     - "dark:bg-[#212121] dark:text-gray-300"
   - Return only the HTML string, no code blocks or explanations
   - No JSX syntax, only plain HTML with className
   - For tables, write out each row manually

4. If result contains multiple rows, show them as static table rows or list items
   DO NOT USE LOOPS - Write out each row manually

Question: {question}
SQL Result: {result}
Analysis: {analysis}

Answer:
<div className="p-4 bg-white dark:bg-[#212121] text-black dark:text-gray-300">
  <!-- your static HTML content based on the result and analysis here -->
</div>"""
)


ANALYSIS_PROMPT_FOR_CHART = PromptTemplate.from_template(
   """Given the following user question, corresponding SQL query, and SQL result, provide a short analysis.
    You are an expert data analyst who excels at interpreting SQL results and providing meaningful insights. 
    

   1.Identify the trend and analyze what user say about the data
   2. Don not write too longs answer.
   3. Highlight the key findings.
   4. Include Quantitative analysis if needed.

    Here is the chart information:

    Here is the SQL query:
    {query}

    Here is the SQL result:
    {result}

    Analysis:
    """
)
   #  {chart_info}

ANSWER_PROMPT_FOR_CHART = PromptTemplate.from_template(
"""Given the following user question, corresponding SQL result, and analysis, generate a response.
You are a frontend engineer specializing in Tailwind CSS and ReactJS.

Create a STATIC user-facing response wrapped in HTML elements using Tailwind CSS classes.

STRICT RULES - VIOLATIONS ARE NOT ALLOWED:
1. ABSOLUTELY NO JAVASCRIPT:
   - NO map(), forEach, or any loops
   - NO array methods
   - NO conditional statements or ternary operators
   - NO variables or constants
   - NO functions or event handlers
   - NO dynamic content or templating

2. HTML/CSS ONLY:
   - Use "className" attribute instead of "class"
   - Use only static HTML elements (<div>, <p>, <table>, etc.)
   - Use Tailwind CSS classes for styling
   - All data must be directly written out, not programmatically generated

3. FORMAT:
   - Wrap everything in a single <div> tag
   - The top-level <div> must include the following Tailwind CSS classes to enable light and dark mode:
     - "dark:bg-[#212121] dark:text-gray-300"
   - Return only the HTML string, no code blocks or explanations
   - No JSX syntax, only plain HTML with className
   - For tables, write out each row manually

4. If result contains multiple rows, show them as static table rows or list items
   DO NOT USE LOOPS - Write out each row manually

Question: {question}
Analysis: {analysis}

Answer:
<div className="p-4 bg-white dark:bg-[#212121] text-black dark:text-gray-300">
  <!-- your static HTML content based on the result and analysis here -->
</div>"""
)

ANALYSIS_PROMPT = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, provide a detailed analysis.
    You are an expert data analyst who excels at interpreting SQL results and providing meaningful insights.

    ANALYSIS REQUIREMENTS:
    1. CONTEXT UNDERSTANDING:
       - Acknowledge the specific intent of the user's question
       - Identify the key metrics being analyzed

    2. DATA INTERPRETATION:
       - Highlight key findings from the results
       - Identify patterns, trends, or anomalies
       - Compare values where relevant
       - Point out any notable highs or lows

    3. INSIGHTS DELIVERY:
       - Provide business-relevant interpretations
       - Explain what the numbers actually mean
       - Draw connections between different data points
       - Suggest potential implications

    4. RESPONSE STRUCTURE:
       - Start with a summary of findings
       - Break down the details
       - Provide specific examples from the data where necessary
       - End with key takeaways

    5. TONE AND STYLE:
       - Be clear and professional
       - Use natural, conversational language
       - Avoid technical jargon unless necessary
       - Be specific with numbers and comparisons

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Analysis: """
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
<div className="p-4 bg-white dark:bg-[#212121] text-black dark:text-gray-300">
  <!-- your static HTML content based on the result -->
</div
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
   <div class="p-4 text-black dark:text-gray-300 rounded-xl shadow-lg">
     <div class="space-y-4">
       <h2 class="text-xl font-semibold text-red-600 dark:text-red-400">
         Access Denied
       </h2>
       <p class="text-gray-700 dark:text-gray-200">
         Your current role
         <span class="font-semibold text-black dark:text-white">'{role}'</span>
         does not have permission to access data from the following table(s):
       </p>
       <div class="p-3 rounded-md border border-gray-200 dark:border-gray-700">
         <code class="text-sm font-mono text-gray-800 dark:text-gray-300">
           '{restricted_tables}'
         </code>
       </div>
       <p class="text-sm text-gray-600 dark:text-gray-400">
         If you believe this is an error or require access to these resources, please contact your administrator or review your assigned role's permissions.
       </p>
     </div>
   </div>
"""
