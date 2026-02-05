from llama_index.llms.ollama import Ollama
from typing import Dict
import ast
import time
import logging

logger = logging.getLogger(__name__)
    
class OllamaModel:
    def __init__(self):
        self.llm = Ollama(model="llama3.1:8b",
         request_timeout=360.0,
         temperature=0.6,
         additional_kwargs={
            "num_ctx": 4096
            }
         )
    
    def inference(self, prompt_text):
        return self.llm.complete(prompt_text).text

    def extract_knowledge_simultaneously(self, text_chunk: str) -> Dict:
        """Extracts entities and relationships in a single pass with cross-validation"""
        
        prompt = f"""
        You are an expert knowledge extraction system. Your task is to extract comprehensive entities with detailed descriptions AND meaningful relationships from the text.

        STEP 1 - ENTITY EXTRACTION:
        Focus on extracting the most important entities with rich, contextual descriptions.
        
        Entity types to focus on:
        - People (full names, roles, professions)
        - Organizations (companies, institutions, teams, clubs)
        - Places (locations, countries, cities)
        - Events (tournaments, competitions, transfers)
        - Time references (months, seasons, dates)
        - Concepts (contracts, fees, transfer windows)

        STEP 2 - RELATIONSHIP EXTRACTION:
        Extract meaningful relationships that connect the entities you identified.
        Focus on relationships that provide valuable knowledge graph connections.

        Text to analyze:
        \"\"\"
        {text_chunk}
        \"\"\"

        CRITICAL REQUIREMENTS:
        1. Entity descriptions must be detailed and only include information explicitly present in the text.
            Do not assume, infer, or add facts not stated in the text.(10 words minimum, strictly based on text)
        2. Use consistent entity names throughout (prefer full names over nicknames)
        2.1. if an entity name is a synonim or abreviation for another entity name make a relationship showing it 
        3. Extract 12-15 entities maximum for quality over quantity
        4. Extract 15-20 relationships that only reference entities in your entities dictionary
        5. Ensure every relationship tuple has exactly 3 elements
        6. If nicknames exist, mention them in the description but use the primary name as the key
        7. keep the relation between subject entity and object entity short
        8. Write only complete tuples, not tuples with less than three elements and no empty elements in the tuple

        VALIDATION RULES:
        - Every relationship subject and object MUST exist as a key in the entities dictionary
        - Entity names should be normalized (proper capitalization, no articles)
        - Relationship predicates should be specific and meaningful
        - No incomplete tuples in relationships

        Return format (EXACT structure required):
        {{
            "entities": {{
                "Primary Entity Name": "Detailed description with context only from the text, including role, significance, and relevant details mentioned"
            }},
            "relationships": [
                ("Subject Entity", "verb/phrase", "Object Entity")
            ]
        }}
        
        Return ONLY the Python dictionary, no explanations or comments.
        """
        
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Extraction attempt {attempt + 1}/{max_retries}")
                
                response = self.inference(prompt)
                logger.info("Simultaneous extraction response: " + response)
                
                # Parse the response
                result = ast.literal_eval(response.strip())
                return result
            
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed because of: {e}")
                
                if attempt < max_retries - 1:  # If not the last attempt
                    wait_time = 5 
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time) 
                    logger.info(f"Retrying...")
                else:  # Last attempt failed
                    logger.error(f"All {max_retries} attempts failed due to timeout")
                    return {"entities": {}, "relationships": []}  
            
        return {"entities": {}, "relationships": []}
    
    
    def _validate_and_clean_extraction(self, result: Dict) -> Dict:
        """Validate and clean the extracted knowledge"""
        
        entities = result.get("entities", {})
        relationships = result.get("relationships", [])
        
        # Track all entities mentioned in relationships
        entities_in_relationships = set()
        valid_relationships = []
        
        for rel in relationships:
            if isinstance(rel, tuple) and len(rel) == 3:
                subject, predicate, obj = rel
                if subject and predicate and obj:
                    entities_in_relationships.add(subject)
                    entities_in_relationships.add(obj)
                    valid_relationships.append(rel)
        
        # Add missing entities that appear in relationships
        for entity_name in entities_in_relationships:
            if entity_name not in entities:
                entities[entity_name] = f"Entity extracted from relationships: {entity_name}"
                logger.info(f"Added missing entity from relationships: {entity_name}")
        
        return {
            "entities": entities,
            "relationships": valid_relationships
        }
