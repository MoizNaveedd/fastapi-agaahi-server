from langchain_community.utilities import SQLDatabase
from app.config import settings

def get_database():
    return SQLDatabase.from_uri(settings.DB_URI)

db = get_database() 