import requests
from bs4 import BeautifulSoup
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
import logging

logger = logging.getLogger(__name__)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", ". ", "! ", "? ", "; ", "\n", " "],
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
    logger.info(f"extract_from_url")
    
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 1. Try to find main article content
    main = soup.find('main')
    if not main:
        logger.warning("No <main> tag found, falling back to <article>")
        main = soup.find('article')
    
    # 2. Remove unwanted elements 
    unwanted_tags = ['figure', 'figcaption', 'script', 'style', 'aside', 'noscript', 'footer']
    for tag in main.find_all(unwanted_tags):
        tag.decompose()
    
    # 3. Extract text from tags 
    tags_to_include = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'li', 'blockquote', 'pre','code', 'strong', 'em', 'b', 'i', 'u',
    'mark', 'span', 'small', 'time','summary', 'address']
    structured_parts = []
    
    for tag in main.find_all(tags_to_include):
        text = tag.get_text(separator=" ", strip=True)
        if text:
            # Ensure tags end with punctuation so the text is coherent
            if tag.name != 'p':
                if not text.endswith(('.', '?', '!', ':', ';')):
                    text += '.'
            structured_parts.append(text)

    text = " ".join(structured_parts)

    # 4. Clean whitespace
    cleaned_text = ' '.join(text.split())
    
    logger.info(f"Extracted and cleaned text: {cleaned_text}")

    # 5. Clean and Split into chunks
    cleaned_text = clean_text_for_chunking(text)
    split_docs = text_splitter.create_documents([cleaned_text], metadatas=[{"source": url}])
    return split_docs

def clean_text_for_chunking(text):
    # Remove duplicate sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    unique_sentences = []
    seen = set()
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and sentence not in seen and len(sentence) > 15:
            unique_sentences.append(sentence)
            seen.add(sentence)
    
    text = ' '.join(unique_sentences)
    
    # Remove author/date patterns
    text = re.sub(r'By\s+[A-Za-z\s-]+\|\s*[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}\.?', '', text)
    text = re.sub(r'\|\s*[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}\.?', '', text)

    # Fix duplicate words
    text = re.sub(r'\b([A-Z][a-z]+)\s*\.\s*\1\b', r'\1', text)
    
    # Clean spacing
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()