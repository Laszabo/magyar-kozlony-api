from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF

app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "OK"}

@app.post("/chunk")
async def chunk_pdf(request: Request):
    try:
        pdf_bytes = await request.body()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        chunk_size = 40
        chunks = []

        for i in range(0, len(doc), chunk_size):
            pages = doc[i:i + chunk_size]
            text = "".join(page.get_text() for page in pages).strip()

            if text:  # Only keep non-empty chunks
                chunks.append({
                    "chunk_id": f"chunk_{(i // chunk_size) + 1:03}",
                    "start_page": i + 1,
                    "end_page": min(i + chunk_size, len(doc)),
                    "text": text,
                    "tokens_estimate": int(len(text.split()) * 1.3)
                })

        doc.close()

        return JSONResponse(content={
            "document_title": "uploaded_via_binary.pdf",
            "total_chunks": len(chunks),
            "chunks": chunks
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
