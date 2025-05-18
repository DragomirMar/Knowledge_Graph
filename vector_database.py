from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from uuid import uuid4

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
)

class VectorDatabase:
    
    def __init__(self):   
        self.vector_store = Chroma(
            collection_name="my_collection",
            embedding_function=embeddings,   
        )
    
    def add_document_triplets(self, triples, source):
        documents = [Document(page_content=triplet, metadata={"source":source}, id=idx) for idx, triplet in enumerate(triples)]
        uuids = [str(uuid4()) for _ in range(len(documents))]
        self.vector_store.add_documents(documents=documents, ids=uuids)
