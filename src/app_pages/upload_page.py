import streamlit as st
from services.document_processing_service import process_documents


if "uploaded_documents" not in st.session_state:
    st.session_state.uploaded_documents = []

if "uploaded_urls" not in st.session_state:
    st.session_state.uploaded_urls = []

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


def render_page():
    st.title("📤 Upload Documents")

    col1, col2 = st.columns(2)
    
    # PDF Upload Section 
    with col1:
        st.subheader("📄 Upload PDF Files")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            key=f"pdf_uploader_{st.session_state.uploader_key}"
        )
        
        if uploaded_files:
            for file in uploaded_files:
                if file not in st.session_state.uploaded_documents:
                    st.session_state.uploaded_documents.append(file)
        
        if st.session_state.uploaded_documents:
            st.success(f"📁 {len(st.session_state.uploaded_documents)} PDF file(s) ready for processing")

            for i, doc in enumerate(st.session_state.uploaded_documents):
                col_name, col_remove = st.columns([3, 1])
                with col_name:
                    st.write(f"• {doc.name}")
                with col_remove:
                    if st.button("❌", key=f"remove_pdf_{i}"):
                        # Remove from our list
                        st.session_state.uploaded_documents.pop(i)

                        # Force reset of file uploader widget
                        st.session_state.uploader_key += 1
                        st.rerun()           
    
    # URL Upload Section
    with col2:
        st.subheader("🌐 Add URLs")
        url_input = st.text_input("Enter URL", placeholder="https://example.com/article")
        
        if st.button("Add URL"):
            if url_input and url_input not in st.session_state.uploaded_urls:
                st.session_state.uploaded_urls.append(url_input)
                st.success(f"URL added: {url_input}")
                st.rerun()
            elif url_input in st.session_state.uploaded_urls:
                st.warning("URL already added")
            else:
                st.error("Please enter a valid URL")
        
        if st.session_state.uploaded_urls:
            st.success(f"🔗 {len(st.session_state.uploaded_urls)} URL(s) ready for processing")
            for i, url in enumerate(st.session_state.uploaded_urls):
                col_url, col_remove = st.columns([3, 1])
                with col_url:
                    st.write(f"• {url}")
                with col_remove:
                    if st.button("❌", key=f"remove_url_{i}"):
                        st.session_state.uploaded_urls.remove(url)
                        st.rerun()
    
    st.markdown("---")
    col_process, col_clear = st.columns([2, 1])
    
    # Processing section
    with col_process:
        if st.button("🚀 Process All Documents", type="primary", use_container_width=True):
            if st.session_state.uploaded_documents or st.session_state.uploaded_urls:
                with st.spinner("Processing documents... This may take a few minutes."):
                    try:
                        entity_count, relationship_count = process_documents(
                            st.session_state.uploaded_documents,
                            st.session_state.uploaded_urls
                        )
                        
                        # Clear session state
                        st.session_state.uploaded_documents = []
                        st.session_state.uploaded_urls = []
                        
                        st.success(f"""
                            ✅ **Documents processed successfully!**
                            
                            - **{entity_count}** entities extracted
                            - **{relationship_count}** relationships created
                            """)
                    except Exception as e:
                        st.error(f"Processing failed with error: {str(e)}")
            else:
                st.error("Please add at least one PDF file or URL before processing.")
    
    with col_clear:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.uploaded_documents = []
            st.session_state.uploaded_urls = []
            
            # Reset uploader
            st.session_state.uploader_key += 1
            st.rerun()