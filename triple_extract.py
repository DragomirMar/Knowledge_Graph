from llm import OllamaModel
from typing import List, Tuple
import ast

class TripleExtractor:
    def __init__(self):
        self.llm = OllamaModel()

    def extract_triples(self, text_chunk: str) -> List[Tuple[str, str, str]]:
#         prompt = f"""
# Extract entities and relations in a format that lets me generate a knowledge graph using python.
# Structure the entities and relationships as triples in the form (Subject, Predicate, Object) from the following text:

# \"\"\" 
# {text_chunk}
# \"\"\"

# - The subject and object should be concise named entities (person, place, organization, etc.), not full sentences.
# - The predicate should be a verd or verb phrase that accurately describes the relationship.

# Return the output as a Python list of tuples.  Return ONLY a valid Python list of tuples. DO NOT include any explanation or formatting.
# Example:
# [
#     ("Entity1", "relationship", "Entity2"),
#     ...
# ]
# """
        prompt = f"""
        You are an expert in information extraction. Your task is to extract structured knowledge from a paragraph in the form of subject-relationship-object triples which will be used later in a knowledge graph, both for visualisation and storing in a vector database. 
        Extract as many triples as needed to have a clear view of all relations between the objects.

        Each triple should describe a clear relationship between two entities, written like:
        (subject, relationship, object)

        Keep relationships simple and meaningful, but at the same time as close to the text as possible, don't use your own interpretation. Also remove adjectives from the relationships (i.e. "keen" instead of "extremely keen")
        The subject and object should be concise named entities (person, place, organization, etc.), not full sentences. 
        If some entities (subjects or objects) are synonyms to other entities connect them with simple relationships (like i.e. "is",...) so that they can be shown in a graph that they mean the same thing.

        Here is the paragraph:
        \"\"\" 
        {text_chunk}
        \"\"\" 

        Return the output as a Python list of tuples.  Return ONLY a valid Python list of tuples. DO NOT include any explanation or formatting.
        Example:
        [
            ("Entity1", "relationship", "Entity2"),
            ...
        ]
        Output only the list of triples.
        """

        response = self.llm.prompt(prompt)
        print("Response: " + response)
        try:
            # Evaluate the response as a Python list safely
            triples = ast.literal_eval(response.strip())
            if isinstance(triples, list) and all(isinstance(t, tuple) and len(t) == 3 for t in triples):
                return triples
        except Exception as e:
            print("⚠️ Failed to parse triples:", e)

        return []
    
    
    
#             prompt = f"""
# You are an expert in information extraction. Your task is to extract structured knowledge from the paragraph below in the form of subject–predicate–object triples, which will be used to build a knowledge graph for visualization and storage in a vector database.

# Guidelines:
# - Each triple must be structured as: (subject, relationship, object)
# - The **subject** and **object** must be short, meaningful named entities (e.g., person, organization, location), never full sentences.
# - The **relationship** must be a concise verb phrase (1–4 words max) directly connecting the two entities. Do not include names or entities in the relationship.
# - Do not include adjectives or modifiers in the relationship (e.g., use "is", not "is extremely popular").
# - Do not infer or summarize; only extract what is clearly stated in the text.
# - If two entities refer to the same thing (e.g., "Los Blancos" and "Real Madrid"), link them using a simple triple like ("Los Blancos", "is", "Real Madrid").

# Input:
# \"\"\" 
# {text_chunk}
# \"\"\"

# Output Format:
# Return only a **valid Python list of tuples**, like:
# [
#     ("Entity1", "relationship", "Entity2"),
#     ...
# ]
# Do not include any explanation, formatting, or additional text. Output only the list of triples.
# """