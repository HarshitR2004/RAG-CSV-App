# Standard library imports
import os
from typing import List, Optional

# Third-party imports
import numpy as np
import pandas as pd
import torch
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="RAG CSV API",
    description="API for managing and querying CSV files using RAG",
    version="1.0.0"
)

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.rag_csv_db

# Initialize models
model = SentenceTransformer('all-MiniLM-L6-v2')
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
llm_model = AutoModelForCausalLM.from_pretrained("google/flan-t5-small")

# Pydantic models for request/response
class QueryRequest(BaseModel):
    file_id: str
    query: str

class FileResponse(BaseModel):
    file_id: str
    file_name: str

@app.post("/upload", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read CSV file
        df = pd.read_csv(file.file)
        
        # Convert DataFrame to string for embedding
        text_content = df.to_string()
        
        # Generate embeddings
        embeddings = model.encode(text_content)
        
        # Store in MongoDB
        file_data = {
            "file_name": file.filename,
            "content": df.to_dict(orient="records"),
            "embeddings": embeddings.tolist()
        }
        
        result = await db.files.insert_one(file_data)
        
        return {"file_id": str(result.inserted_id), "message": "Upload successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files", response_model=dict)
async def get_files():
    try:
        files = await db.files.find().to_list(length=None)
        file_list = [
            {"file_id": str(file["_id"]), "file_name": file["file_name"]}
            for file in files
        ]
        return {"files": file_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=dict)
async def query_file(query_request: QueryRequest):
    try:
        # Get file from database
        file = await db.files.find_one({"_id": ObjectId(query_request.file_id)})
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Generate query embedding
        query_embedding = model.encode(query_request.query)
        
        # Convert embeddings to numpy arrays for similarity calculation
        file_embedding = np.array(file["embeddings"])
        query_embedding = query_embedding.reshape(1, -1)
        
        # Calculate similarity score
        similarity_score = cosine_similarity(query_embedding, file_embedding.reshape(1, -1))[0][0]
        
        # Get the content from the file
        content = file["content"]
        
        # Prepare context for LLM
        context = str(content)  # Convert content to string format
        prompt = f"Based on the following data:\n{context}\n\nQuestion: {query_request.query}\nAnswer:"
        
        # Generate response using LLM
        inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        with torch.no_grad():
            outputs = llm_model.generate(
                **inputs,
                max_length=150,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.95
            )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return {
            "response": response,
            "similarity_score": float(similarity_score)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/file/{file_id}", response_model=dict)
async def delete_file(file_id: str):
    try:
        result = await db.files.delete_one({"_id": ObjectId(file_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="File not found")
        return {"message": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)