import streamlit as st
import pandas as pd
import requests
import json

# Configure page settings
st.set_page_config(page_title="RAG CSV App", layout="wide")
st.title("RAG CSV Application")

# Initialize session state
if 'files' not in st.session_state:
    st.session_state.files = []

# Function to fetch all files
def fetch_files():
    try:
        response = requests.get("http://localhost:8000/files")
        if response.status_code == 200:
            st.session_state.files = response.json()["files"]
        else:
            st.error("Failed to fetch files")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# File Upload Section
st.header("Upload CSV File")
upload_file = st.file_uploader("Choose a CSV file", type="csv")
if upload_file:
    files = {"file": upload_file}
    try:
        response = requests.post("http://localhost:8000/upload", files=files)
        if response.status_code == 200:
            st.success("File uploaded successfully!")
            fetch_files()  # Refresh file list after upload
        else:
            st.error("Failed to upload file")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# File List and Query Section
st.header("Query CSV Files")

# Fetch files on page load
if not st.session_state.files:
    fetch_files()

if st.session_state.files:
    # File selection
    file_options = {f"{file['file_name']} (ID: {file['file_id']})" : file['file_id'] 
                   for file in st.session_state.files}
    selected_file = st.selectbox("Select a file to query", options=list(file_options.keys()))
    selected_file_id = file_options[selected_file]
    
    # Query input
    query = st.text_area("Enter your query")
    if st.button("Submit Query"):
        if query:
            try:
                response = requests.post(
                    "http://localhost:8000/query",
                    json={"file_id": selected_file_id, "query": query}
                )
                if response.status_code == 200:
                    result = response.json()
                    st.subheader("Query Results")
                    st.write(result)
                else:
                    st.error("Failed to process query")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a query")
else:
    st.info("No files available. Please upload a CSV file first.")