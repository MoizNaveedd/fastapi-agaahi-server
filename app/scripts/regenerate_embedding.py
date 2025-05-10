import os
import sys

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from app.services.embedding_service import LocalKnowledgeBaseService

def main():
    print("Starting knowledge base update...")
    kb_service = LocalKnowledgeBaseService()
    kb_service.regenerate_embeddings()
    print("Knowledge base update completed!")

if __name__ == "__main__":
    main()