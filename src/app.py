import streamlit as st
from io import BytesIO
import logging
from extract_text import extract_from_url, extract_from_pdf
from llm import OllamaModel
import entity_manager as em
from database_manager import DBManager as dbm
from logger_config import setup_logging
from graph_visualizer import get_graph_visualizer

setup_logging()
logger = logging.getLogger(__name__)

def process_documents():
    """Process all uploaded documents and URLs"""
    with st.spinner("Processing documents... This may take a few minutes."):
        try:
            llm = OllamaModel()
            all_chunks = []
            
            # Process PDFs
            for pdf_file in st.session_state.uploaded_documents:
                try:
                    file_like = BytesIO(pdf_file.read())
                    chunks = extract_from_pdf(file_like)
                    all_chunks.extend(chunks)
                    logger.info(f"Extracted {len(chunks)} chunks from {pdf_file.name}")
                except Exception as e:
                    st.error(f"Error processing {pdf_file.name}: {str(e)}")
                    continue
            
            # Process URLs
            for url in st.session_state.uploaded_urls:
                try:
                    chunks = extract_from_url(url)
                    all_chunks.extend(chunks)
                    logger.info(f"Extracted {len(chunks)} chunks from {url}")
                except Exception as e:
                    st.error(f"Error processing {url}: {str(e)}")
                    continue
            
            if all_chunks:
                # Extract entities and relationships
                entities_and_relationships = em.extract_entities_and_relationships_from_chunks(
                    all_chunks, llm
                )
                
                # Store in database
                entities = entities_and_relationships["entities"]
                relationships = entities_and_relationships["relationships"]
                
                entity_count = 0
                relationship_count = 0
                
                for name, description in entities.items():
                    try:
                        dbm.create_entity(name, description)
                        entity_count += 1
                    except Exception as e:
                        logger.warning(f"Error creating entity {name}: {str(e)}")
                
                for subject, predicate, obj in relationships:
                    try:
                        dbm.create_relationship(subject, predicate, obj)
                        relationship_count += 1
                    except Exception as e:
                        logger.warning(f"Error creating relationship {subject}-{predicate}-{obj}: {str(e)}")
                
                # Clear session state
                st.session_state.uploaded_documents = []
                st.session_state.uploaded_urls = []
                
                # Show success message
                st.success(f"""
                ✅ **Documents processed successfully!**
                
                - **{entity_count}** entities extracted
                - **{relationship_count}** relationships created
                """)
                
            else:
                st.warning("No content could be extracted from the provided documents.")
                
        except Exception as e:
            st.error(f"An error occurred during processing: {str(e)}")
            logger.error(f"Processing error: {str(e)}")

def show_add_entity_form():
    """Show form to add a new entity"""
    st.subheader("Add New Entity")
    
    with st.form("add_entity_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            entity_name = st.text_input("Entity Name*", placeholder="Enter entity name...")
            entity_description = st.text_area("Description", placeholder="Enter entity description...", height=100)
        
        with col2:
            st.write("")  # Space
            submitted = st.form_submit_button("Add Entity", type="primary", use_container_width=True)
        
        if submitted:
            if entity_name.strip():
                try:
                    result = dbm.create_entity(entity_name.strip(), entity_description.strip())
                    if result == "Entity already exists":
                        st.warning(f"Entity '{entity_name}' already exists!")
                    else:
                        st.success(f"Entity '{entity_name}' created successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error creating entity: {str(e)}")
            else:
                st.error("Entity name is required!")

def show_add_relationship_form(current_entity_name):
    """Show form to add a new relationship for the current entity"""
    st.subheader("Add New Relationship")
    
    # Get all entities for the object dropdown
    try:
        all_entities = dbm.get_all_entities()
        entity_names = [entity['name'] for entity in all_entities if entity['name'] != current_entity_name]
    except Exception as e:
        st.error(f"Error loading entities: {str(e)}")
        return
    
    # Create radio button outside the form so it shows object type options 
    relationship_type = st.radio(
        "Object Type:", 
        ["Existing Entity", "New Entity"], 
        horizontal=True,
        key=f'relationship_type_{current_entity_name}'
    )
    
    with st.form(f"add_relationship_form_{current_entity_name}", clear_on_submit=True):
        st.write(f"**Subject:** {current_entity_name}")
        
        predicate = st.text_input("Predicate*", placeholder="e.g., 'is related to', ...")
        
        # Show object entity input based on relationship type
        if relationship_type == "Existing Entity":
            if entity_names:
                object_entity = st.selectbox("Select Object Entity*", [""] + entity_names)
                object_description = ""
            else:
                st.info("No other entities available. Create a new entity instead.")
                object_entity = ""
                object_description = ""
        else:  # New Entity
            object_entity = st.text_input("New Object Entity*", placeholder="Enter new entity name...")
            object_description = st.text_area("Object Description", placeholder="Description for new entity...", height=100)
        
        submitted = st.form_submit_button("Add Relationship", type="primary")
        
        if submitted:
            if predicate.strip() and object_entity.strip():
                try:
                    dbm.create_relationship(current_entity_name, predicate.strip(), object_entity.strip())
                    
                    # If a new entity created, update its description
                    if relationship_type == "New Entity" and object_description.strip():
                        try:
                            dbm.update_entity_description(object_entity.strip(), object_description.strip())
                        except Exception as e:
                            logger.warning(f"Could not update description for new entity: {str(e)}")
                    
                    st.success(f"Relationship created: {current_entity_name} → {predicate} → {object_entity}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating relationship: {str(e)}")
            else:
                st.error("Predicate and Object Entity are required!")

def show_entity_detail():
    """Show detailed view of a single entity"""
    if not st.session_state.selected_entity:
        st.error("No entity selected")
        return
    
    entity_name = st.session_state.selected_entity
    
    try:
        # Get entity details
        entity = dbm.get_entity_by_name(entity_name)
        if not entity:
            st.error("Entity not found")
            return
        
        st.title(f"📋 Entity: {entity['name']}")
        
        # Entity editing section
        with st.expander("✏️ Edit Entity", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                new_name = st.text_input("Entity Name", value=entity['name'])
                new_description = st.text_area("Description", value=entity['description'], height=100)
            
            with col2:
                st.write("")  # Space
                if st.button("💾 Save Changes", type="primary"):
                    try:
                        if new_name != entity['name']:
                            dbm.update_entity_name(entity['name'], new_name)
                            st.session_state.selected_entity = new_name
                        
                        if new_description != entity['description']:
                            dbm.update_entity_description(new_name, new_description)
                        
                        st.success("Entity updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating entity: {str(e)}")
            
                if 'confirm_delete_entity' not in st.session_state:
                    st.session_state.confirm_delete_entity = False

                if not st.session_state.confirm_delete_entity:
                    if st.button("🗑️ Delete Entity", type="secondary"):
                        st.session_state.confirm_delete_entity = True
                        st.rerun()
                else:
                    st.warning("⚠️ This will permanently delete the entity and its relationships.")
                    
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("✅ Confirm Delete"):
                            try:
                                dbm.delete_entity(entity['name'])
                                st.success("Entity deleted!")
                                st.session_state.current_page = "main"
                                st.session_state.selected_entity = None
                                st.session_state.confirm_delete_entity = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting entity: {str(e)}")

                    with col_cancel:
                        if st.button("❌ Cancel"):
                            st.session_state.confirm_delete_entity = False
                            st.rerun()
        
        # Add new relationship section
        st.markdown("---")
        with st.expander("➕ Add New Relationship"):
            show_add_relationship_form(entity_name)
            
        # Relationships section
        st.markdown("---")
        st.subheader("🔗 Existing Relationships")
        
        relationships = dbm.get_relationships_by_entity(entity_name)
        
        if relationships:
            st.markdown(f"Found **{len(relationships)}** relationships involving this entity:")
            
            for i, rel in enumerate(relationships):
                with st.expander(f"{rel['subject']} → {rel['predicate']} → {rel['object']}"):
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        st.write(f"**Subject:** {rel['subject']}")
                        st.write(f"**Object:** {rel['object']}")
                    
                    with col2:
                        new_predicate = st.text_input(
                            "Predicate", 
                            value=rel['predicate'], 
                            key=f"pred_{i}"
                        )
                        
                        if st.button("Update Predicate", key=f"update_{i}"):
                            try:
                                dbm.update_relationship_predicate(
                                    rel['subject'], rel['object'], new_predicate
                                )
                                st.success("Predicate updated!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating predicate: {str(e)}")
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_{i}"):
                            try:
                                dbm.delete_relationship(rel['subject'], rel['object'])
                                st.success("Relationship deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting relationship: {str(e)}")
        else:
            st.info("No relationships found for this entity.")
        
        # Graph visualization section
        st.markdown("---")
        st.subheader("📊 Graph View")
        
        col_graph, col_nav = st.columns([4, 1])
        
        with col_graph:
            # Show mini graph centered on this entity
            graph_viz = get_graph_visualizer()
            graph_viz.render_mini_graph(entity_name)
        
        with col_nav:
            st.write("")  # Space
            if st.button("🔍 View Full Graph", type="secondary"):
                # Set this entity as selected in the full graph
                graph_viz.initialize_graph_data()
                if not st.session_state.graph_data["nodes"]:
                    graph_viz.load_data_from_database()
                
                # Find and select this entity in the graph
                for node_id, props in st.session_state.graph_data["nodes"].items():
                    if props.get("original_name") == entity_name:
                        st.session_state.graph_data["selected_node"] = node_id
                        break
                
                # Navigate to graph page
                st.session_state.current_page = "main"
                st.session_state.last_main_page = "📊 Knowledge Graph"
                st.rerun()
            
    except Exception as e:
        st.error(f"Error loading entity details: {str(e)}")


st.set_page_config(
    page_title="Knowledge Graph Manager",
    page_icon="🧠",
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
if 'browse_entities' not in st.session_state:
    st.session_state.browse_entities = "main"

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
    show_entity_detail()
elif page == "📤 Upload Documents":
    st.title("📤 Upload Documents")
    st.markdown("Add PDF files or URLs to extract knowledge and build your graph.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Upload PDF Files")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            key="pdf_uploader"
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
                        st.session_state.uploaded_documents.remove(doc)
                        st.rerun()
                        
    
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
    
    # Processing section
    st.markdown("---")
    col_process, col_clear = st.columns([2, 1])
    
    with col_process:
        if st.button("🚀 Process All Documents", type="primary", use_container_width=True):
            if st.session_state.uploaded_documents or st.session_state.uploaded_urls:
                process_documents()
            else:
                st.error("Please add at least one PDF file or URL before processing.")
    
    with col_clear:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.uploaded_documents = []
            st.session_state.uploaded_urls = []
            st.rerun()

elif page == "🔍 Browse Entities":
    st.title("🔍 Browse Entities")
    
    # Add New Entity Section
    with st.expander("➕ Add New Entity", expanded=False):
        show_add_entity_form()
    
    st.markdown("---")
    
    # Search and controls
    col_search, col_delete = st.columns([3, 1])

    with col_search:
        search_query = st.text_input("🔍 Search entities...", placeholder="Type to search entities")

    with col_delete:
        # Add empty space to align with the text input
        st.write("")
        
        if 'confirm_delete' not in st.session_state:
            st.session_state.confirm_delete = False

        if not st.session_state.confirm_delete:
            if st.button("🗑️ Delete All Entities", type="secondary"):
                st.session_state.confirm_delete = True
                st.rerun()
        else:
            st.warning("⚠️ This will delete **all** entities and relationships. Are you sure?")
            if st.button("✅ Confirm Delete"):
                try:
                    dbm.drop_collection_entities()
                    dbm.drop_collection_relationships()
                    st.success("All entities and relationships deleted!")
                    st.session_state.confirm_delete = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting entities: {str(e)}")
            if st.button("❌ Cancel"):
                st.session_state.confirm_delete = False
                st.rerun()
    
    # Get and display entities
    try:
        entities = dbm.get_all_entities()
        
        if entities:
            # Filter entities based on search
            if search_query:
                filtered_entities = [e for e in entities if search_query.lower() in e['name'].lower()]
            else:
                filtered_entities = entities
            
            st.markdown(f"### Found {len(filtered_entities)} entities")
            
            # Display entities in a grid with consistent sizing
            cols = st.columns(3)
            for i, entity in enumerate(filtered_entities):
                with cols[i % 3]:
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            border: 1px solid #ddd; 
                            border-radius: 10px; 
                            padding: 15px; 
                            margin: 10px 0;
                            background-color: #f9f9f9;
                            cursor: pointer;
                            height: 140px;
                            display: flex;
                            flex-direction: column;
                            justify-content: space-between;
                        ">
                            <div>
                                <h4 style="
                                    margin: 0 0 10px 0; 
                                    color: #1f2937;
                                    font-size: 18px;
                                    font-weight: 600;
                                    line-height: 1.2;
                                    overflow: hidden;
                                    text-overflow: ellipsis;
                                    white-space: nowrap;
                                    max-height: 38px;
                                ">{entity['name']}</h4>
                                <p style="
                                    margin: 0; 
                                    color: #666; 
                                    font-size: 14px;
                                    line-height: 1.3;
                                    overflow: hidden;
                                    text-overflow: ellipsis;
                                    display: -webkit-box;
                                    -webkit-line-clamp: 3;
                                    -webkit-box-orient: vertical;
                                    max-height: 54px;
                                ">
                                    {entity['description'][:100]}{'...' if len(entity['description']) > 100 else ''}
                                </p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"View Details", key=f"entity_{i}", use_container_width=True):
                            st.session_state.selected_entity = entity['name']
                            st.session_state.current_page = "entity_detail"
                            st.rerun()
        else:
            st.info("No entities found. Upload some documents to get started!")
            
    except Exception as e:
        st.error(f"Error loading entities: {str(e)}")

elif page == "📊 Knowledge Graph":
    st.title("📊 Knowledge Graph Visualization")
    
    graph_viz = get_graph_visualizer()
    
    # Load data from database on first visit or when requested
    if not st.session_state.get('graph_data', {}).get('nodes'):
        with st.spinner("Loading graph data from database..."):
            success, message = graph_viz.load_data_from_database()
            if success:
                st.success(message)
            else:
                st.error(message)
    
    st.markdown("---")
    
    # Show refresh controls
    graph_viz.show_refresh_controls()
    
    # Render the main graph
    graph_viz.render_graph()
    
    # Show sidebar options
    with st.sidebar:
        graph_viz.show_graph_statistics()
        st.markdown("---")
        graph_viz.show_node_editor()

# Custom CSS for better styling
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
    }
    
    .metric-container {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    
    .entity-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9f9f9;
        transition: all 0.3s ease;
    }
    
    .entity-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)