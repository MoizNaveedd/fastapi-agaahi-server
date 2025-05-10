import json
from typing import List
import re

class ContextService:
    def __init__(self, knowledge_base_path: str = "app/data/vector_store/texts.json"):
        with open(knowledge_base_path, 'r') as f:
            self.knowledge_base = json.load(f)
    
    def _preprocess_text(self, text: str) -> str:
        """Convert text to lowercase and remove punctuation for better matching"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def get_relevant_context(self, query: str, max_results: int = 2) -> List[str]:
        """
        Get relevant context by matching keywords in the query with knowledge base entries
        Returns the top matching entries
        """
        query = self._preprocess_text(query)
        query_words = set(query.split())
        
        # Score each knowledge base entry based on keyword matches
        scored_entries = []
        for entry in self.knowledge_base:
            entry_text = self._preprocess_text(entry)
            entry_words = set(entry_text.split())
            
            # Calculate simple word overlap score
            matching_words = query_words.intersection(entry_words)
            score = len(matching_words)
            
            if score > 0:
                scored_entries.append((score, entry))
        
        # Sort by score and return top results
        scored_entries.sort(reverse=True)
        return [entry for score, entry in scored_entries[:max_results]] 