from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
import os

app = FastAPI()

@app.post("/chunk")
async def chunk_pdf(file: UploadFile = File(...)):
    try:
        # Save the uploaded PDF to a temporary file
        temp_path = "temp.pdf"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # Open the PDF using fitz (PyMuPDF)
        doc = fitz.open(temp_path)
        chunk_size = 40
        final_chunks = []

        for i in range(0, len(doc), chunk_size):
            merged_text = ""
            for page in doc[i:i + chunk_size]:
                merged_text += page.get_text()

            final_chunks.append({
                "chunk_id": f"chunk_{(i // chunk_size) + 1:03}",
                "start_page": i + 1,
                "end_page": min(i + chunk_size, len(doc)),
                "text": merged_text.strip(),
                "tokens_estimate": int(len(merged_text.split()) * 1.3)
            })

        # Clean up
        doc.close()
        os.remove(temp_path)

        # Filter out empty chunks
        final_chunks = [chunk for chunk in final_chunks if chunk['text']]

        return JSONResponse(content={
            "document_title": file.filename,
            "total_chunks": len(final_chunks),
            "chunks": final_chunks
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
