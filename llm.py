from llama_index.llms.ollama import Ollama

class OllamaModel:
    def __init__(self):
        self.llm = Ollama(model="llama3.1:8B", request_timeout=120.0, temperature=0.7)
    
    def prompt(self, prompt_text):
        return self.llm.complete(prompt_text).text
