import streamlit as st
import logging
from database_manager import DBManager as dbm
from graph_visualisation.graph_visualizer import render_mini_graph

logger = logging.getLogger(__name__)

def show_relationship_creation_form(current_entity_name):
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

def render_page():
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
            show_relationship_creation_form(entity_name)
            
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
        
        render_mini_graph(entity_name)
          
    except Exception as e:
        st.error(f"Error loading entity details: {str(e)}")