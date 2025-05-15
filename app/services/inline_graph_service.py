import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from langchain.chains import create_sql_query_chain
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from fastapi import APIRouter, HTTPException, Request
from app.core.init import initialize_llm
from app.services.query_service import get_table_details
from app.models.schemas import ChartInfo

# from app.services.query_service import get_llm
# chart_prompt = f"""
# You are an expert in SQL-based data visualization.
# Extract the necessary details for chart plotting from the user's query.
# Your response MUST be structured as follows:
# - `chart_type`: One of ["bar", "line", "pie"]
# - `x_axis`: The name of the column to use for the x-axis.
# - `y_axis`: The name of the column to use for the y-axis.
# - `query`: construct the syntactically correct query by checking table and relations from:


# {table_details_context}
# and query should return summarized results: for example take this query:
# SELECT
#     DATE_FORMAT(order_date, '%Y-%m') AS Month,  -- Aggregate by month
#     SUM(total_price) AS Total_Sales  -- Summarized sales data
# FROM orders
# WHERE YEAR(order_date) = YEAR(CURDATE()) - 1
# GROUP BY Month
# ORDER BY Month;


# make sure the column names for x and y axis exist in the database schema aand are correct
# IMPORTANT: If the query is only about visualization (e.g., "show this in a graph"), return an empty response.
# e.q  "Also plot a graph" should not return a query so your response should be NULL
# If you cannot extract data, return an empty list for `data` but still specify `chart_type`, `x_axis`, and `y_axis`.
# """

table_details_context = get_table_details()

def get_llm():
    """Get LLM instance from app state"""
    return initialize_llm()
    # return request.app.state.llm

# below is working fine
chart_prompt = """
You are an expert in SQL-based data visualization.

Your task is to extract the necessary chart metadata and valid SQL queries from the user's intent, based on a chart type explicitly provided by the user.

---
### Instructions:
- Your output MUST be in **valid JSON** format.
- The JSON should be an **array of objects**, where each object matches this structure exactly:
  - `chart_type`: One of ["bar", "line", "pie"] — this will be explicitly provided by the user.
  - `x_axis`: The name of the column to use for the x-axis.
  - `y_axis`: The name of the column to use for the y-axis.
  - `query`: A syntactically correct SQL query using the provided schema.
- Use `CURDATE()` if "today" is mentioned.


Schema of the database:
{table_details_context}


User Question: {question}

---

### Guidelines:
1. Use only the `chart_type` explicitly given by the user. Do not infer or change the chart type.
2. The chart must have:
   - A valid `x_axis` and `y_axis` column from the schema.
   - A `query` that uses the correct tables and relationships.
3. The SQL `query` must:
   - Perform aggregation (e.g., using SUM, COUNT).
   - Use appropriate `GROUP BY` and `ORDER BY` clauses.
4. If the user request does not support the specified chart type due to lack of valid fields or data, return a single object with all values as `null`:
"""


import json

def clean_and_parse_json(json_input: str) -> List[ChartInfo]:

    # Remove unwanted characters like ```json and ```
    cleaned_json = json_input.strip().replace("```json", "").replace("```", "")

    try:
        # Parse the cleaned JSON string into a Python list
        chart_info_list = json.loads(cleaned_json)

        # Validate and convert each item into a ChartInfo object using Pydantic
        return [ChartInfo(**item) for item in chart_info_list]

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []
    except Exception as e:
        print(f"Error during parsing and validation: {e}")
        return []




def generate_chart_info(question):
    llm = get_llm()
    # generate_query_chain = create_sql_query_chain(llm, db, final_prompt)
    response = llm.invoke(chart_prompt.format(question=question,table_details_context=table_details_context)).content.strip()
    return response


def generate_sql_query(question, llm, db, final_prompt):
    generate_query_chain = create_sql_query_chain(llm, db, final_prompt)
    response = generate_query_chain.invoke({"question": question})
    return response.get("query", "")

def process_chart_request(question: str, history, llm, db, final_prompt):

    chart_keywords = ["line", "bar", "pie"]
    detected_chart_type = next((kw for kw in chart_keywords if kw in question.lower()), None)

    if not detected_chart_type:
        return None

    # extract_chart_chain = create_extraction_chain_pydantic(ChartInfo, llm, system_message=chart_prompt)
    # print(extract_chart_chain)
    # chart_info_list = extract_chart_chain.invoke({"input": question})
    # print(chart_info_list)

    # graphtype =

    unclean_chart_info_list = generate_chart_info(question)
    # print("unclean_chart_info_list",unclean_chart_info_list)
    chart_info_list = clean_and_parse_json(unclean_chart_info_list)
    # print("chart_info_list",chart_info_list)
    # parsed_str = chart_info_list.strip().replace("print(", "").rstrip(")")
    # chart_info = literal_eval(parsed_str)


    # print(chart_info)
    # print("chart_info_list",chart_info_list)
    if isinstance(chart_info_list, list) and chart_info_list:
        chart_info = chart_info_list[0]
    else:
        chart_info = None

    # print("chart_info",chart_info)
    # If no valid chart details are found, fall back to the previous history (only if it makes sense)
    # if not chart_info or not chart_info.query:
    #     last_result = history.messages[-1].content if history.messages  else None
    #     print(last_result)
    #     if last_result:
    #         history_context = "\n".join([msg.content for msg in history.messages[-3:]])  # Last 3 messages for context
    #         chart_info_list = extract_chart_chain.invoke({"input": f"{history_context}\n{last_result}"})
    #         if isinstance(chart_info_list, list) and chart_info_list:
    #             chart_info = chart_info_list[0]

    # if not chart_info:
    #     print("No chart data available.")
    #     return None

    # if not chart_info.query:
    #     chart_info.query = generate_sql_query(question, llm, db, final_prompt)

    return chart_info

import ast

import pandas as pd
import json
import re
                # from datetime import datetime
import json
import pandas as pd
from datetime import datetime
# def fetch_data_from_db(query, db, chart_info):
#     try:
#         result = db.run(query)
#         print("Raw result:", result)
#         print("Result type:", type(result))
        
#         if result is None:
#             print("Query returned None.")
#             return pd.DataFrame()

#         # If result is a string containing list of tuples with datetime
#         if isinstance(result, str):
#             try:
#                 # Extract datetime and value pairs using string manipulation
                

#                 # Parse the string to extract datetime and values
#                 pattern = r"datetime\.datetime\((\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\),\s*(\d+)"
#                 matches = re.findall(pattern, result)
                
#                 formatted_data = []
#                 for match in matches:
#                     year, month, day, hour, minute, second, value = map(int, match)
#                     dt = datetime(year, month, day, hour, minute, second)
#                     formatted_data.append((dt.strftime('%Y-%m-%d %H:%M:%S'), value))

#                 if not formatted_data:
#                     print("No valid data extracted from string")
#                     return pd.DataFrame()

#                 df = pd.DataFrame(formatted_data, columns=[chart_info.x_axis, chart_info.y_axis])
#                 print("Final DataFrame:\n", df.head())
#                 return df

#             except Exception as e:
#                 print(f"Error parsing string result: {e}")
#                 traceback.print_exc()
#                 return pd.DataFrame()

#         # If result is already a DataFrame
#         if isinstance(result, pd.DataFrame):
#             return result

#         # Ensure result is a list
#         if not isinstance(result, list):
#             result = [result]

#         print("Processed result:", result)

#         # Extract data based on x_axis and y_axis
#         formatted_data = []
#         for item in result:
#             try:
#                 # If item is a tuple or list with exactly 2 elements
#                 if isinstance(item, (tuple, list)) and len(item) == 2:
#                     x_value, y_value = item

#                     # Handle datetime conversion
#                     if isinstance(x_value, datetime):
#                         x_value = x_value.strftime('%Y-%m-%d %H:%M:%S')
#                     if isinstance(y_value, datetime):
#                         y_value = y_value.strftime('%Y-%m-%d %H:%M:%S')

#                     formatted_data.append((x_value, y_value))
#                 else:
#                     print(f"Skipping invalid data format: {item}")
#                     continue

#             except Exception as e:
#                 print(f"Error processing record {item}: {str(e)}")
#                 continue

#         if not formatted_data:
#             print("No valid data after processing")
#             return pd.DataFrame()

#         # Create DataFrame
#         df = pd.DataFrame(formatted_data, columns=[chart_info.x_axis, chart_info.y_axis])
#         print("Final DataFrame:\n", df.head())
#         return df

#     except Exception as e:
#         print(f"Error in fetch_data_from_db: {str(e)}")
#         print(f"Error type: {type(e)}")
#         import traceback
#         traceback.print_exc()
#         return pd.DataFrame()

import json
import pandas as pd
import re
import ast
from datetime import datetime

def fetch_data_from_db(query, db, chart_info):
    try:
        result = db.run(query)
        print("Raw result:", result)
        print("Result type:", type(result))

        if result is None:
            print("Query returned None.")
            return pd.DataFrame()

        # Handle stringified results
        if isinstance(result, str):
            try:
                formatted_data = []
                
                # Case 1: datetime.datetime format with time
                if "datetime.datetime" in result:
                    pattern = r"datetime\.datetime\((\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\),\s*(\d+)"
                    matches = re.findall(pattern, result)
                    
                    if matches:
                        for match in matches:
                            year, month, day, hour, minute, second, value = map(int, match)
                            # Format as date only since we don't need the time
                            dt = f"{year}-{month:02d}-{day:02d}"
                            formatted_data.append((dt, value))
                    else:
                        print("No matches found with datetime pattern")
                        return pd.DataFrame()

                # Case 2: datetime.date format
                elif "datetime.date" in result:
                    pattern = r"datetime\.date\((\d+),\s*(\d+),\s*(\d+)\),\s*(\d+)"
                    matches = re.findall(pattern, result)
                    
                    if matches:
                        for match in matches:
                            year, month, day, value = map(int, match)
                            dt = f"{year}-{month:02d}-{day:02d}"
                            formatted_data.append((dt, value))
                    else:
                        print("No matches found with datetime.date pattern")
                        return pd.DataFrame()

                # Case 3: Regular tuples
                else:
                    parsed = ast.literal_eval(result)
                    if isinstance(parsed, list) and all(isinstance(t, (tuple, list)) and len(t) == 2 for t in parsed):
                        for x_value, y_value in parsed:
                            if isinstance(x_value, datetime):
                                x_value = x_value.strftime('%Y-%m-%d')
                            formatted_data.append((x_value, y_value))
                    else:
                        print("String did not evaluate to expected list of tuples.")
                        return pd.DataFrame()

                if not formatted_data:
                    print("No valid data extracted from string")
                    return pd.DataFrame()

                df = pd.DataFrame(formatted_data, columns=[chart_info.x_axis, chart_info.y_axis])
                print("Final DataFrame:\n", df.head())
                return df

            except Exception as e:
                print(f"Error parsing string result: {e}")
                import traceback
                traceback.print_exc()
                return pd.DataFrame()

        # If result is already a DataFrame
        if isinstance(result, pd.DataFrame):
            return result

        # Ensure result is a list
        if not isinstance(result, list):
            result = [result]

        print("Processed result:", result)

        # Extract data based on x_axis and y_axis
        formatted_data = []
        for item in result:
            try:
                if isinstance(item, (tuple, list)) and len(item) == 2:
                    x_value, y_value = item

                    # Handle datetime.date objects
                    if isinstance(x_value, datetime.date):
                        x_value = x_value.strftime('%Y-%m-%d')
                    elif isinstance(x_value, datetime):
                        x_value = x_value.strftime('%Y-%m-%d')  # Only keep the date part

                    formatted_data.append((x_value, y_value))
                else:
                    print(f"Skipping invalid data format: {item}")
                    continue

            except Exception as e:
                print(f"Error processing record {item}: {str(e)}")
                continue

        if not formatted_data:
            print("No valid data after processing")
            return pd.DataFrame()

        df = pd.DataFrame(formatted_data, columns=[chart_info.x_axis, chart_info.y_axis])
        print("Final DataFrame:\n", df.head())
        return df

    except Exception as e:
        print(f"Error in fetch_data_from_db: {str(e)}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()
import os
import base64
from io import BytesIO

def plot_chart(chart_info, db):
    if not chart_info:
        print("No chart data available.")
        return None

    data = fetch_data_from_db(chart_info.query, db, chart_info)

    if data.empty:
        print("No data available for the chart.")
        return None

    if chart_info.x_axis not in data.columns or chart_info.y_axis not in data.columns:
        print(f"Missing expected columns: {chart_info.x_axis}, {chart_info.y_axis}")
        print("Data received:", data.head())
        return None

    plt.figure(figsize=(10, 5))

    if chart_info.chart_type.lower() == "bar":
        sns.barplot(x=data[chart_info.x_axis], y=data[chart_info.y_axis], palette="magma")
    elif chart_info.chart_type.lower() == "line":
        sns.lineplot(x=data[chart_info.x_axis], y=data[chart_info.y_axis], color="violet", linewidth=2)
    elif chart_info.chart_type.lower() == "pie":
        data.set_index(chart_info.x_axis)[chart_info.y_axis].plot.pie(
            autopct="%1.1f%%", colors=['#ff6666', '#ffcc99', '#99ff99', '#66b3ff']
        )
        plt.ylabel("")  # Pie chart doesn't need y-axis label
    else:
        print(f"Unsupported chart type: {chart_info.chart_type}")
        return None

    if chart_info.chart_type.lower() != "pie":
        plt.xlabel(chart_info.x_axis)
        plt.ylabel(chart_info.y_axis)

    plt.title(f"{chart_info.chart_type.capitalize()} Chart of {chart_info.y_axis} by {chart_info.x_axis}")

    # Create a directory to save the image
    # os.makedirs("charts", exist_ok=True)

    # Generate filename
    # safe_x = chart_info.x_axis.replace(" ", "_").lower()
    # safe_y = chart_info.y_axis.replace(" ", "_").lower()
    # filename = f"{chart_info.chart_type.lower()}_chart_{safe_y}_by_{safe_x}.png"
    # save_path = os.path.join("charts", filename)

    # Save plot to disk
    # plt.savefig(save_path, bbox_inches="tight")

    # Save plot to buffer for Base64 conversion
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    # print(f"Chart saved at {save_path}")
    # print(img_base64)
    return img_base64,data