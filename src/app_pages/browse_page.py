import streamlit as st
from database.database_manager import DBManager as dbm

def create_entity_creation_form():
    st.subheader("Add New Entity")
    
    with st.form("add_entity_form", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            entity_name = st.text_input("Entity Name*", placeholder="Enter entity name...")
            entity_description = st.text_area("Description", placeholder="Enter entity description...", height=100)
        
        with col2:
            st.write("")  # Empty space for alignment
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

def render_page():
    st.title("🔍 Browse Entities")
    
    # Add New Entity Section
    with st.expander("➕ Add New Entity", expanded=False):
        create_entity_creation_form()
    
    st.markdown("---")
    
    # Search and controls
    col_search, col_delete = st.columns([3, 1])

    with col_search:
        search_query = st.text_input("🔍 Search entities...", placeholder="Type to search entities")

    with col_delete:
        st.write("") # Empty space to align with the text input
        
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
    
    # Display entities
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