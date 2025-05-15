from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List

class Role(Enum):
    Owner = "owner"
    Admin = "admin"
    Engineer = "data_engineer"
    DataAnalyst = "data_analyst"

class QueryRequest(BaseModel):
    user_prompt: str
    role: str
    allowed_tables: List[str]

class ConversationNameRequest(BaseModel):
    user_prompt: str

class ChartInfo(BaseModel):
    chart_type: str = Field(description="The type of chart to generate (e.g., Bar, Line, Pie).")
    x_axis: str = Field(description="The attribute for the x-axis.")
    y_axis: str = Field(description="The attribute for the y-axis.")
    query: str = Field(description="SQL query to fetch relevant data.")

class DashboardRequest(BaseModel):
    user_prompt: str
    role: str
    chart_id: int 

class EditorQuery(BaseModel):
    question: str
    role: str
    allowed_tables: List[str]

class KnowledgeBaseQuery(BaseModel):
    question: str
