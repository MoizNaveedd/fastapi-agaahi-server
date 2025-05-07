import pandas as pd
import base64
from io import BytesIO
import matplotlib.pyplot as plt
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