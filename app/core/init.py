from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

def initialize_llm():
    """Initialize and return LLM instance"""
    return ChatGoogleGenerativeAI(
        model="models/gemini-1.5-flash-8b",
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY,
    )

# Initialize shared resources
llm = initialize_llm() 