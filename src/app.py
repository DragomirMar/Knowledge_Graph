import streamlit as st
from database.database_manager import DBManager as dbm
from app_pages import browse_page, entity_page, graph_page, upload_page

from configuration.logger_config import setup_logging
setup_logging()

st.set_page_config(
    page_title="Knowledge Graph",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'uploaded_documents' not in st.session_state:
    st.session_state.uploaded_documents = []
if 'uploaded_urls' not in st.session_state:
    st.session_state.uploaded_urls = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = "main"
if 'selected_entity' not in st.session_state:
    st.session_state.selected_entity = None

# Sidebar navigation
st.sidebar.title("Knowledge Graph")
st.sidebar.markdown("---")

# Initialize page state if not set
if "page" not in st.session_state:
    st.session_state.page = "📤 Upload Documents"

PAGES = ["📤 Upload Documents", "🔍 Browse Entities", "📊 Knowledge Graph"]

if st.session_state.current_page == "main":
    # Use session_state.page to set default index
    default_index = PAGES.index(st.session_state.page)
    page = st.sidebar.selectbox("Navigation", PAGES, index=default_index)

    # Update session state when user changes selection
    st.session_state.page = page

else:
    # Show current entity info when viewing entity details
    st.sidebar.markdown(f"**Viewing Entity:**")
    st.sidebar.markdown(f"📋 {st.session_state.selected_entity}")
    if st.sidebar.button("← Back to Browse Entities"):
        st.session_state.current_page = "main"
        st.session_state.selected_entity = None
        st.session_state.page = "🔍 Browse Entities"  
        st.rerun()
    else:
        page = "entity_detail"

# Show statistics in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Statistics")
try:
    entity_count = dbm.get_entity_count()
    relationship_count = dbm.get_relationship_count()
    st.sidebar.metric("Entities", entity_count)
    st.sidebar.metric("Relationships", relationship_count)
except Exception as e:
    st.sidebar.error("Database connection error")

# Main content based on selected page
if st.session_state.current_page == "entity_detail":
    entity_page.render_page()
elif page == "📤 Upload Documents":
    upload_page.render_page()
elif page == "🔍 Browse Entities":
    browse_page.render_page()
elif page == "📊 Knowledge Graph":
    graph_page.render_page()