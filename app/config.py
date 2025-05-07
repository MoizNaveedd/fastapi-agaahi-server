import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Database settings
    DB_URI = os.getenv("DB_URI", "mysql+pymysql://avnadmin:AVNS_Aq4bxZ77DFtERGsnEnQ@mysql-1aede23-iomechs-1b2b.i.aivencloud.com:12234/defaultdb")
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyAPYAWyUv3dQR4PlaEU9lxUBKCJFZMsoAs")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "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")
    
    # LangChain settings
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
    
    # Model settings
    GEMINI_MODEL = "models/gemini-1.5-flash-8b"
    
    # Chart storage
    CHART_DIR = "charts"

settings = Settings() 