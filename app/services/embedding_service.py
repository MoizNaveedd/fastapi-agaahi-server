from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np
import faiss
import os
import json

class LocalKnowledgeBaseService:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.texts = []
        self.vector_dimension = 384  # dimension for this model
        self.index_path = "app/data/vector_store/faiss_index"
        self.texts_path = "app/data/vector_store/texts.json"
        self.initialize_knowledge_base()

    def get_relevant_context(self, question: str, k: int = 3) -> str:
        """Get relevant context from knowledge base without formatting response"""
        try:
            # First check if we have any texts
            if not self.texts or len(self.texts) == 0:
                print("Warning: No texts available in knowledge base")
                return "I don't have any information in my knowledge base yet."
    
            # Get relevant information
            question_embedding = self.model.encode([question])
            
            # Ensure k is not larger than the number of texts
            k = min(k, len(self.texts))
            
            # Search in FAISS index
            distances, indices = self.index.search(
                np.array(question_embedding).astype('float32'), 
                k
            )
            
            # Validate indices
            valid_indices = [idx for idx in indices[0] if 0 <= idx < len(self.texts)]
            
            if not valid_indices:
                print("Warning: No valid indices found")
                return "I couldn't find relevant information for your question."
                
            # Get relevant texts and combine them
            relevant_texts = [self.texts[idx] for idx in valid_indices]
            
            # Debug information
            print(f"Found {len(relevant_texts)} relevant texts")
            print(f"Indices: {valid_indices}")
            
            return "\n\n".join(relevant_texts)
                
        except Exception as e:
            print(f"Error in get_relevant_context: {str(e)}")
            return "I encountered an error while searching for information."

    def initialize_knowledge_base(self):
        """Initialize or load the knowledge base"""
        if os.path.exists(self.index_path) and os.path.exists(self.texts_path):
            # Load existing index and texts
            self.index = faiss.read_index(self.index_path)
            with open(self.texts_path, 'r', encoding='utf-8') as f:
                self.texts = json.load(f)
        else:
            # Create new index
            self.index = faiss.IndexFlatL2(self.vector_dimension)
            self.load_knowledge_base()

    def load_knowledge_base(self):
        """Load and process knowledge base documents"""
        knowledge_base_dir = "app/data/knowledge_base"
        
        # Read all text files from the knowledge base directory
        for root, _, files in os.walk(knowledge_base_dir):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Split content into chunks (simple splitting by paragraphs)
                        chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
                        self.texts.extend(chunks)

        # Create embeddings for all texts
        embeddings = self.model.encode(self.texts)
        
        # Add to FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Save index and texts
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.texts_path, 'w', encoding='utf-8') as f:
            json.dump(self.texts, f)

    def query_knowledge_base(self, question: str, k: int = 3) -> str:
        """Query the knowledge base"""
        try:
            # Create embedding for the question
            question_embedding = self.model.encode([question])
            
            # Search in FAISS index
            distances, indices = self.index.search(
                np.array(question_embedding).astype('float32'), 
                k
            )
            
            # Get relevant texts
            relevant_texts = [self.texts[idx] for idx in indices[0]]
            
            # Combine relevant texts into a response
            response = self._format_response(relevant_texts)
            return response
        except Exception as e:
            return f"Error querying knowledge base: {str(e)}"

    def _format_response(self, relevant_texts: List[str]) -> str:
        """Format the response from relevant texts"""
        # Simple concatenation with formatting
        formatted_response = []
        for i, text in enumerate(relevant_texts, 1):
            formatted_response.append(text)
        
        return "\n\n".join(formatted_response)

    def add_new_knowledge(self, text: str):
        """Add new knowledge to the base"""
        # Create embedding for new text
        embedding = self.model.encode([text])
        
        # Add to index and texts
        self.index.add(np.array(embedding).astype('float32'))
        self.texts.append(text)
        
        # Save updated index and texts
        faiss.write_index(self.index, self.index_path)
        with open(self.texts_path, 'w', encoding='utf-8') as f:
            json.dump(self.texts, f)
    
    def regenerate_embeddings(self, knowledge_base_dir="app/data/knowledge_base"):
        """Regenerate embeddings for new or updated knowledge base"""
        print("Starting embeddings regeneration...")
        
        # Reset existing data
        self.texts = []
        self.index = faiss.IndexFlatL2(self.vector_dimension)
        
        # Read all text files from the knowledge base directory
        for root, _, files in os.walk(knowledge_base_dir):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    print(f"Processing file: {file_path}")
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Split content into chunks (simple splitting by paragraphs)
                        chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
                        self.texts.extend(chunks)
                        print(f"Added {len(chunks)} chunks from {file}")
        
        # print(f"Total texts to embed: {len(self.texts)}")
        
        # Create embeddings for all texts
        embeddings = self.model.encode(self.texts, show_progress_bar=True)
        
        # Add to FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Save index and texts
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.texts_path, 'w', encoding='utf-8') as f:
            json.dump(self.texts, f)
            
        print("Embeddings regeneration completed!")
        print(f"Saved {len(self.texts)} text chunks with embeddings")   
        print(f"Total texts to embed: {len(self.texts)}")
        
        # Create embeddings for all texts
        embeddings = self.model.encode(self.texts, show_progress_bar=True)
        
        # Add to FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Save index and texts
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.texts_path, 'w', encoding='utf-8') as f:
            json.dump(self.texts, f)
            
        print("Embeddings regeneration completed!")
        print(f"Saved {len(self.texts)} text chunks with embeddings")