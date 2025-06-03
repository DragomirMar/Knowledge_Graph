from llama_index.llms.ollama import Ollama
from typing import List, Tuple
import ast
import requests

    
class OllamaModel:
    def __init__(self):
        self.llm = Ollama(model="llama3.1:8B", request_timeout=120.0, temperature=0.7)
    
    def inference(self, prompt_text):
        return self.llm.complete(prompt_text).text

    def extract_triples(self, text_chunk: str) -> List[Tuple[str, str, str]]:
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
        
        Extract only the 20 most important triples.
        """

        response = self.inference(prompt)
        print("Response: " + response)
        print("END Response")
        try:
            # Evaluate the response as a Python list safely
            triples = ast.literal_eval(response.strip())

            # Only keep tuples that are of length 3 and triples with no none values
            if isinstance(triples, list):
                valid_triples = [
                    t for t in triples 
                    if isinstance(t, tuple) and len(t) == 3 and all(part is not None for part in t)
                ]
                return valid_triples
        except Exception as e:
            print("⚠️ Failed to parse triples:", e)


class HuggingFaceLLM:
    API_URL = "https://router.huggingface.co/novita/v3/openai/chat/completions"
    headers = {
        "Authorization": "Bearer add_token_here",
    }

    def query(payload):
        response = requests.post(HuggingFaceLLM.API_URL, 
                                headers=HuggingFaceLLM.headers, 
                                json=payload)
        return response.json()

    def inference(self, prompt_text):
        response = HuggingFaceLLM.query({
            "messages": [
                {
                    "role": "user",
                    "content": prompt_text
                }
            ],
            "model": "deepseek/deepseek-v3-0324",
            "max_tokens": 2048
        })

        print(f"RESPONSE: {response}")
        return response["choices"][0]["message"]["content"]


    def extract_triples(self, text: str) -> List[Tuple[str, str, str]]:
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
        {text}
        \"\"\" 

        Return the output as a Python list of tuples.  Return ONLY a valid Python list of tuples. DO NOT include any explanation or formatting.
        Example:
        [
            ("Entity1", "relationship", "Entity2"),
            ...
        ]
        Output only the list of triples.
        """

        response = self.inference(prompt)
        print("Response: ", response)
        try:
            # Evaluate the response as a Python list safely
            triples = ast.literal_eval(response.strip())

            # Only keep tuples that are of length 3 and triples with no none values
            if isinstance(triples, list):
                valid_triples = [
                    t for t in triples 
                    if isinstance(t, tuple) and len(t) == 3 and all(part is not None for part in t)
                ]
                return valid_triples
        except Exception as e:
            print("⚠️ Failed to parse triples:", e)