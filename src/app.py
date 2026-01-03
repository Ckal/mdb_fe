
# Streamlit app for the frontend
import streamlit as st
from typing import Dict, List
import requests
import json

# Backend API endpoint
API_BASE_URL = "https://chris4k-mdb.hf.space"  # Change this to your deployed backend URL

def fetch_documents():
    response = requests.get(API_BASE_URL)
    try:
        response_json = response.json()
        return response_json.get("documents", [])
    except requests.exceptions.JSONDecodeError:
        print("Invalid JSON response:", response.text)
        return []  # Return an empty list if the response is invalid



def index_content(doc_type: str, source: str, config: Dict):
    """Index content through the backend API."""
    payload = {"doc_type": doc_type, "source": source, "config": config}
    response = requests.post(f"{API_BASE_URL}/index", json=payload)
    return response.json()

def delete_document(doc_id: str):
    """Delete a document by its ID."""
    response = requests.delete(f"{API_BASE_URL}/delete?doc_id={doc_id}")
    return response.json()

def search_documents(query: str, top_k: int = 5):
    """Search documents through the backend API."""
    payload = {"query": query, "top_k": top_k}
    response = requests.post(f"{API_BASE_URL}/search", json=payload)
    return response.json()

# === Streamlit Frontend ===
st.title("ChromaDB Document Manager 📚")

# Sidebar for Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Add Document", "Search"])

# --- Home Page: List and Manage Documents ---
if page == "Home":
    st.header("Indexed Documents")
    documents = fetch_documents()

    if not documents:
        st.info("No documents indexed yet.")
    else:
        for doc in documents:
            with st.expander(f"Document ID: {doc['doc_id']}"):
                st.write("**Metadata:**")
                st.json(doc)

                # Delete Button
                if st.button(f"Delete {doc['doc_id']}"):
                    result = delete_document(doc['doc_id'])
                    st.success(f"Deleted: {result['doc_id']}")

# --- Add Document Page ---
elif page == "Add Document":
    st.header("Add a New Document")
    doc_type = st.selectbox("Document Type", ["pdf", "webpage", "manual"])
    source = st.text_input("Source (URL for webpage, file path for PDF, or manual text)")
    config = st.text_area(
        "Configuration (JSON)", 
        value=json.dumps({"chunk_size": 1000, "chunk_overlap": 200}, indent=4)
    )

    if st.button("Index Document"):
        try:
            config_dict = json.loads(config)
            result = index_content(doc_type, source, config_dict)
            st.success(f"Document indexed: {result['doc_id']}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# --- Search Page ---
elif page == "Search":
    st.header("Search Documents")
    query = st.text_input("Enter your search query")
    top_k = st.number_input("Number of Results", min_value=1, max_value=10, value=5)

    if st.button("Search"):
        try:
            results = search_documents(query, top_k)
            st.write("**Results:**")
            for idx, res in enumerate(results["results"]):
                st.markdown(f"**Result {idx + 1}:**")
                st.write(res)
        except Exception as e:
            st.error(f"Error: {str(e)}")

