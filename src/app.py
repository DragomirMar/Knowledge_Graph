import streamlit as st
from extract_text import *
from llm import *
from vector_database import VectorDatabase
from plot_graph import GraphPlot

llm = OllamaModel()
db = VectorDatabase()
gp = GraphPlot()

def save_files_to_db(uploaded_files):
    st.write("Saving files to DB...")
    for file in uploaded_files:
        split_docs = extract_from_pdf(file)
        split_docs = split_docs[:5] # Limit to first 5 chunks for testing purposes
        
        all_triples = []
        for doc in split_docs:
            doc_text_content = doc.page_content
            print(f"Processing chunk: {doc_text_content[:100]}...")# Print a preview of the chunk
            
            triples = llm.extract_triples(doc_text_content)
            print(f"Extracted triples: {triples}")
            
            all_triples.extend(triples)
        
        print(f"All triples extracted: {all_triples}")
        db.add_document_triplets(all_triples, file.name)
        print("Documents added successfully")

def clear_database():
    st.write("Database cleared.")
    db.clear_database()

def show_sources():
    sources = db.get_sources()
    st.write("Sources in the database:")
    for source in sources:
        st.write(f"- {source}")

def process_url(url):
    st.write(f"Processing URL: {url}")
    extracted_chunks = extract_from_url(url)  
    extracted_chunks = extracted_chunks[:5]  # Limit to first 5 chunks for testing purposes
    
    all_triples = []
    for doc in extracted_chunks:  
        doc_text_content = doc.page_content
        print(f"Processing chunk: {doc_text_content[:100]}...") 
        
        triples = llm.extract_triples(doc_text_content)
        print(f"Extracted triples: {triples}")
  
        all_triples.extend(triples)
    
    print(f"All triples extracted: {all_triples}")
    db.add_document_triplets(all_triples, url)
    print("URL content added successfully")

def show_knowledge_graph():
    all_triples = db.get_all_triplets_by_source()
    image_buffer = gp.plot(all_triples)
    st.image(image_buffer, caption="Knowledge Graph")  

# Title
st.set_page_config(page_title="KG ChatBot")
st.title('Set a Domain')

# PDF Upload
uploaded_files = st.file_uploader("Upload PDF", type="pdf",label_visibility="collapsed", accept_multiple_files=True)    

if st.button("Confirm Files"):
    save_files_to_db(uploaded_files)

# URL Upload 
st.subheader("Add Text via URL")
input_url = st.text_input("Enter URL", placeholder="https://example.com/article")

if st.button("Confirm URL"):
    if input_url.strip():
        process_url(input_url)
    else:
        st.warning("Please enter a valid URL.")


col1, col2 = st.columns([1,1]) 
with col1:
    if st.button("Show Sources"):
        show_sources()

with col2:
    if st.button("Clear Database"):
        clear_database()
            
#Knowledge Garph View
if st.button("Show Graph"):
    show_knowledge_graph()

        
# Chat Bot
st.title('Chat Bot 🤖')

if st.button("🧹", help="Clear chat"):
    st.session_state.messages = []
    st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input field (pinned to bottom automatically)
user_input = st.chat_input("Type your message...")


if user_input:
    # Show user's message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Response
    with st.spinner("KG Bot is thinking..."):
        # Search vector DB
        relevant_triples = db.similarity_search(user_input, k=5)
        print(f"Relevant triples: {relevant_triples}")
        context = "\n".join(relevant_triples)

        # Add context to user query
        enriched_prompt = f"""
            You are a helpful assistant. Use the following context to help answer the user's question.
            Only use the context if it is relevant.
            Summarize your answer in no more than 3 sentences.

            Context:
            {context}

            User Question:
            {user_input}

            Answer:"""

        response_text = llm.inference(enriched_prompt)

    response = f"{response_text}"
    st.chat_message("assistant").markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})