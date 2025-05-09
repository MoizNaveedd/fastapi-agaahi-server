from app.utils.helpers import get_relevant_table_details
from app.models.schemas import DashboardRequest
from app.utils.helpers import extract_selected_tables, validate_table_access
from app.core.init import initialize_llm
import pandas as pd
import json
import re

def get_llm():
    return initialize_llm()

def clean_query(raw_query: str) -> str:
    return re.sub(r"```sql|```", "", raw_query, flags=re.IGNORECASE).strip()


async def set_graph_request(query_request: DashboardRequest, chart_meta_info: list):
    try:
        llm = get_llm()
        print("I am running")
        question = query_request.user_prompt
        role = query_request.role
        chart_id = query_request.chart_id  # assuming you have chart_id in QueryRequest

        # Find the chart meta info by id
        selected_chart_meta = next((chart for chart in chart_meta_info if chart["id"] == chart_id), None)

        # print(selected_chart_meta)
        if not selected_chart_meta:
            raise ValueError(f"No chart found for id: {chart_id}")

        # Now you can use `selected_chart_meta` for further processing
        # print("Selected Chart Meta:", selected_chart_meta)

        # Extract tables and check permissions as before...
        extracted_tables = extract_selected_tables({"question": question}, llm)


        print(extracted_tables)
        # Validate access
        access_valid = validate_table_access(role,extracted_tables)

        # print("here")

        # if not access_valid:
        #   # return err
        #     print("access invalid")
        #     # Handle unauthorized access as before...
        #     pass
        print("here")

        # Enhanced chart detection
        visualization_keywords = ["graph", "chart", "plot", "visual", "visualization", "trend",
                                 "compare", "distribution", "show me", "display"]

        if any(keyword in question.lower() for keyword in visualization_keywords):
            # Use our enhanced chart analysis
            chart_analysis = await analyze_chart_request(
                question=question,
                extracted_tables=extracted_tables,
                chart_meta_info=selected_chart_meta,
                llm=llm
            )

            return chart_analysis;

            if chart_analysis["chart_applicable"]:
              return chart_analysis;
                # Execute the SQL to get data
                # chart_data = execute_sql(chart_analysis["sql_query"])

                # # Transform data to match the chart format
                # transformed_data = transform_data_for_chart(
                #     chart_data,
                #     chart_analysis["recommended_chart"],
                #     chart_analysis["column_mapping"]
                # )

                # # Generate the chart
                # chart_config = {
                #     "chartType": chart_analysis["recommended_chart"]["name"],
                #     "chartData": transformed_data,
                #     "chartTitle": chart_analysis["chart_title"],
                #     "description": chart_analysis["description"]
                # }

                # base64_chart = plot_chart(chart_config, db)

            #     return {
            #         "response": f"""
            #         <div className='p-4'>
            #             <div className='text-lg font-semibold mb-2'>{chart_analysis["chart_title"]}</div>
            #             <div className='text-sm text-gray-600 mb-4'>{chart_analysis["description"]}</div>
            #         </div>
            #         """,
            #         "base64": base64_chart,
            #         "format": "graph",
            #         "chart_type": chart_analysis["recommended_chart"]["name"],
            #         "chart_config": chart_config
            #     }
            # else:
            #     # Return error message for chart creation failures
            #     return {
            #         "response": f"""
            #         <div className='p-4 rounded-md bg-red-50 border border-red-200'>
            #             <div className='text-red-600 font-medium'>Sorry, I couldn't create a chart from that request.</div>
            #             <div className='text-sm text-red-500 mt-1'>{chart_analysis["error_message"]}</div>
            #             <div className='text-sm mt-3'>Try asking for specific metrics and dimensions from the available tables.</div>
            #         </div>
            #         """,
            #         "base64": None,
            #         "format": "graph"
            #     }

        # Rest of the function for handling CSV and regular queries as before...

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

async def analyze_chart_request(question: str, extracted_tables: list, chart_meta_info: dict, llm):
    """
    Analyze if the user's query can be used to plot the given chart type and generate appropriate SQL.

    Args:
        question: The user's prompt/question
        extracted_tables: List of database tables mentioned in the query
        chart_meta_info: Selected chart info dictionary (already picked)

    Returns:
        Dict with analysis results including chart configuration and SQL query
    """
    try:
        sheet_url = "https://docs.google.com/spreadsheets/d/1jdEQre3MzvtM6bu71cN6WQs5-ILnojA1-qCNOF6XSHQ/export?format=csv"
        # Read the Google Sheet into a Pandas DataFrame
        df = pd.read_csv(sheet_url)
        relevant_table_details = get_relevant_table_details(df, extracted_tables)
        chart_name = chart_meta_info["name"].lower()

        # Create a base SQL generation prompt
        sql_prompt_template = f"""
        You are a SQL expert generating queries for MySQL version 8.0.36.
        Use MySQL 8.0.36 syntax and functions when generating queries.

        Generate a SQL query that retrieves data suitable for a {chart_name}
        based on the following user question: "{question}"

        Only use tables from this list: {extracted_tables}.

        Schema Info:
        {relevant_table_details}
        """

        # Customize prompt according to the chart type
        if "pie" in chart_name:
            sql_prompt_template += """
            The query must return:
            - One column for categories/labels (text)
            - One column for numeric values

            Example:
            SELECT category_column, SUM(value_column) as total_value
            FROM table
            GROUP BY category_column
            ORDER BY total_value DESC
            LIMIT 10;
            """

        elif "line" in chart_name:
            sql_prompt_template += """
            The query must return:
            - One column for x-axis (typically dates/time)
            - One or more columns for y-axis (numeric values)

            Example:
            SELECT date_column, measure1, measure2
            FROM table
            WHERE date_column BETWEEN start_date AND end_date
            ORDER BY date_column;
            """

        elif "bar" in chart_name:
            sql_prompt_template += """
            The query must return:
            - One column for categories (x-axis)
            - One or more columns for numeric values (y-axis)

            Example:
            SELECT category_column, SUM(value_column)
            FROM table
            GROUP BY category_column
            ORDER BY SUM(value_column) DESC
            LIMIT 10;
            """

        elif "geo" in chart_name:
            sql_prompt_template += """
            The query must return:
            - One column for geographic names (country, region)
            - One column for numeric values

            Example:
            SELECT region_name, SUM(value_column)
            FROM table
            GROUP BY region_name;
            """

        elif "radar" in chart_name:
            sql_prompt_template += """
            The query must return:
            - One column for categories/dimensions
            - Two or more columns representing different series/entities

            Example:
            SELECT category, AVG(metric1) as entity1, AVG(metric2) as entity2
            FROM table
            GROUP BY category;
            """

        elif "radial" in chart_name:
            sql_prompt_template += """
            The query must return:
            - One column for categories
            - One column for numeric values (e.g., percentage)

            Example:
            SELECT category, value_column
            FROM table
            ORDER BY value_column DESC;
            """

        elif "card" in chart_name:
            sql_prompt_template += """
            The query must return:
            - One aggregated metrics (numeric)

            Example:
            SELECT
                SUM(current_value) as total_current
            FROM table;
            """

        else:
            # fallback if unknown chart type
            sql_prompt_template += """
            The query must return:
            - One column for categories
            - One or more numeric columns for measures
            """

        # Common rules
        sql_prompt_template += f"""

        Use `CURDATE()` when using any date condition/filter.
        Return ONLY the SQL query without any explanations or comments.
        """
        # Do not add line breaks.
        # Add a one letter gap like 'select name'

        # Call LLM to generate query
        uncleaned_query = llm.invoke(sql_prompt_template).content.strip()
        sql_query = clean_query(uncleaned_query)

        # No need for chart analysis anymore. You already know the chart.
        # Just prepare the final response


        chart_analysis_prompt = f"""
        Analyze this SQL query generated for the user question: "{question}"

        SQL Query: {sql_query}

        Based on the SQL query structure and the user's question, determine:
        2. The column(s) structure and how they should be mapped to the chart

        Return a JSON object with this structure:
        {{
            "column_mapping": {{
                "x_axis": "name of column for x-axis/categories",
                "y_axis": ["name(s) of column(s) for y-axis/values"],
                "series": ["if applicable, columns representing different series"]
            }},
            "chart_title": "Suggested title for the chart",
            "description": "Brief explanation of why this chart type is appropriate"
        }}
        """

        chart_analysis_response = llm.invoke(chart_analysis_prompt).content.strip()

        # Parse the JSON response

        # Clean the response to ensure it's valid JSON
        chart_analysis_response = re.sub(r'```json|```', '', chart_analysis_response).strip()
        analysis_result = json.loads(chart_analysis_response)
        print(analysis_result)

        return {
            "chart_applicable": True,
            # "recommended_chart": analysis_result,
            "sql_query": sql_query,
            "column_mapping": analysis_result["column_mapping"],
            "chart_title": analysis_result["chart_title"],
            "description": analysis_result["description"]
        }

    except Exception as e:
        return {
            "chart_applicable": False,
            "error_message": f"Error analyzing chart request: {str(e)}"
        }

