import requests
from bs4 import BeautifulSoup
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", ".", "!", "?", "\n", " "],
        add_start_index=False
    )

def extract_from_pdf(file):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file.getbuffer())
        temp_file.flush() 
        
        docs = PyPDFLoader(temp_file.name).load()
        split_docs = text_splitter.split_documents(docs)
    return split_docs
    
def extract_from_url(url):
    # Send a GET request to the webpage
    response = requests.get(url)
    response.raise_for_status()
    
    # Parse the webpage content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    main = soup.find('main')
    text = main.get_text(separator=" ")

    # Clean up any extra whitespace
    cleaned_text = ' '.join(text.split())
    chunks = text_splitter.create_documents([cleaned_text], metadatas=[{"source": url}])
    
    return chunks
