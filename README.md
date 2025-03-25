# RAG CSV API

A FastAPI-based application for managing and querying CSV files using Retrieval-Augmented Generation (RAG). This system allows users to upload CSV files, store them efficiently in MongoDB, and interact with the data through natural language queries using advanced language models.

## Features

- **CSV File Management**
  - Upload and store CSV files in MongoDB
  - List all uploaded files
  - Delete files when no longer needed
  
- **Advanced Query Capabilities**
  - Natural language querying using RAG
  - Semantic search using Sentence Transformers
  - Response generation using FLAN-T5 language model
  
- **Technical Features**
  - RESTful API with FastAPI framework
  - Asynchronous operations for improved performance
  - MongoDB integration for efficient data storage
  - Streamlit-based user interface
  - Comprehensive error handling
  - Swagger/OpenAPI documentation

## Architecture

The application consists of two main components:
1. **Backend API (FastAPI)**
   - Handles file operations and query processing
   - Manages MongoDB interactions
   - Implements RAG pipeline
   
2. **Frontend (Streamlit)**
   - Provides user-friendly interface
   - Enables file upload and query submission
   - Displays query results


## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/HarshitR2004/RAG-CSV-App
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables in `.env` file:
   ```env
   MONGO_URL=mongodb://localhost:27017
   MODEL_CACHE_DIR=./model_cache
   DEBUG=False
   ```

## Running the Application

1. Start MongoDB server:
   ```bash
   mongod
   ```

2. Start the FastAPI backend:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

3. Start the Streamlit frontend:
   ```bash
   streamlit run streamlit_app.py
   ```
   The UI will be available at `http://localhost:8501`

## API Endpoints

### Upload CSV File
- **POST** `/upload`
- **Input**: CSV file (multipart/form-data)
- **Output**: 
  ```json
  {
    "file_id": "string",
    "message": "Upload successful"
  }
  ```

### List Files
- **GET** `/files`
- **Output**:
  ```json
  {
    "files": [
      {
        "file_id": "string",
        "file_name": "string"
      }
    ]
  }
  ```

### Query File
- **POST** `/query`
- **Input**:
  ```json
  {
    "file_id": "string",
    "query": "string"
  }
  ```
- **Output**:
  ```json
  {
    "response": "string",
    "similarity_score": float
  }
  ```

### Delete File
- **DELETE** `/file/{file_id}`
- **Output**:
  ```json
  {
    "message": "File deleted successfully"
  }
  ```

## Error Handling

| Status Code | Description | Possible Cause | Solution |
|------------|-------------|----------------|-----------|
| 400 | Bad Request | Invalid file format, missing parameters, malformed JSON | Check request format and parameters |
| 401 | Unauthorized | Missing or invalid API key | Provide valid authentication credentials |
| 403 | Forbidden | Insufficient permissions | Request access from administrator |
| 404 | Not Found | File ID doesn't exist, endpoint not found | Verify file ID and API endpoint |
| 413 | Payload Too Large | CSV file exceeds size limit | Reduce file size or split into smaller files |
| 415 | Unsupported Media Type | Invalid file type uploaded | Ensure file is valid CSV format |
| 429 | Too Many Requests | Rate limit exceeded | Implement request throttling |
| 500 | Internal Server Error | Database issues, processing failures | Check server logs and database connection |
| 503 | Service Unavailable | Model server down, maintenance mode | Try again later or contact support |


### Models Used
- **Sentence Transformer**: `all-MiniLM-L6-v2`
- **Language Model**: `google/flan-t5-small`
