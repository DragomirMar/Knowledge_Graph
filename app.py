import streamlit as st

def save_files_to_db(uploaded_files):
    st.write("Saving files to DB...")
    # TODO: Implement file saving logic

def clear_database():
    st.write("Clearing database...")
    # TODO: Implement clearing logic

def process_url(url):
    st.write(f"Processing URL: {url}")
    # TODO: Implement URL processing logic (e.g. fetch and extract text)



# Title
st.set_page_config(page_title="KG ChatBot")
st.title('Set a Domain')

# PDF Upload
uploaded_files = st.file_uploader("Upload PDF", type="pdf",label_visibility="collapsed", accept_multiple_files=True)    

if st.button("Confirm Files"):
    save_files_to_db(uploaded_files)

if st.button("Clear Database"):
    clear_database()

# URL Upload 
st.subheader("Add Text via URL")
input_url = st.text_input("Enter URL", placeholder="https://example.com/article")

if st.button("Confirm URL"):
    if input_url.strip():
        process_url(input_url)
    else:
        st.warning("Please enter a valid URL.")

# Chat Bot
st.title('Knowledge Graph Chat Bot')

if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Custom input field and button (NOT pinned to bottom)
user_input = st.text_input("Type your message:")

if st.button("Send"):
    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        response = f"Echo: {user_input}"
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
"""
 Upload PDF files
 "Confirm" upload e.g. save them to the database

 Input URLs
 On Click "Confirm" save to the database

Show Knowledge Graph


 ChatBot
 Ask question
"""