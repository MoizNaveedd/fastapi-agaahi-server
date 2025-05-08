import os

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://user:pass@localhost:3306/db")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "models/gemini-1.5-flash-8b"  # Change back to this model name 