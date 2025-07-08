from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import fitz  # PyMuPDF
import tempfile
import os

app = FastAPI()

class PdfRequest(BaseModel):
    pdf_url: str

def download_pdf(url: str) -> str:
    if "megtekintes" in url:
        url = url.replace("megtekintes", "letoltes")
    
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Could not download PDF.")
    
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
    with os.fdopen(tmp_fd, 'wb') as tmp_file:
        tmp_file.write(response.content)
    return tmp_path

def extract_chunks(pdf_path: str, chunk_size: int = 40) -> list:
    chunks = []
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)
        for i in range(0, total_pages, chunk_size):
            chunk_text = ""
            for j in range(i, min(i + chunk_size, total_pages)):
                chunk_text += doc[j].get_text()
            chunk_metadata = f"-- Pages {i+1} to {min(i+chunk_size, total_pages)} --\n"
            chunks.append(chunk_metadata + chunk_text)
    return chunks

@app.post("/extract_text")
async def extract_text(data: PdfRequest):
    try:
        pdf_path = download_pdf(data.pdf_url)
        chunks = extract_chunks(pdf_path)
        os.remove(pdf_path)

        if len(chunks) == 1:
            return {"pages": "under_40", "text": chunks[0][:3000] + "..."}
        else:
            return {
                "pages": "over_40",
                "chunk_count": len(chunks),
                "chunks": [chunk[:3000] + "..." for chunk in chunks]  # Trim for preview
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "FastAPI GPT endpoint is up!"}
