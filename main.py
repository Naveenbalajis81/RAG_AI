import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.rag_pipeline import embed_and_store, query_rag
from app.utils import extract_text_from_pdf


app = FastAPI(title="Student Document QA System")
# Upload endpoint
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload PDF or TXT and store in Pinecone."""
    if not (file.filename.endswith(".pdf") or file.filename.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files supported")

    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
        tmp_file.write(await file.read())
        tmp_path = tmp_file.name

    # Extract text
    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(tmp_path)
    else:
        with open(tmp_path, "r", encoding="utf-8") as f:
            text = f.read()

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text extracted from document")

    # Embed & store in Pinecone
    embed_and_store(text)

    return {"status": "success", "message": f"{file.filename} uploaded and indexed"}

# Chat endpoint
@app.post("/chat")
async def chat(query: dict):
    """Answer questions using RAG pipeline."""
    user_query = query.get("query", "").strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    answer = query_rag(user_query)
    return {"answer": answer}
