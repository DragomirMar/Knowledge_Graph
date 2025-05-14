import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TextHandler:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", ".", "!", "?", "\n", " "],
            add_start_index=False
        )

    def extract_from_pdf(self, pdf_file_path):
        docs = PyPDFLoader(file_path=pdf_file_path).load()
        chunks = self.text_splitter.split_documents(docs)
        return chunks
        
    def extract_from_url(self, url):
        # Send a GET request to the webpage
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the webpage content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
       
        main = soup.find('main')
        text = main.get_text(separator=" ")

        # Clean up any extra whitespace
        cleaned_text = ' '.join(text.split())
        chunks = self.text_splitter.create_documents([cleaned_text], metadatas=[{"source": url}])
        
        return chunks
