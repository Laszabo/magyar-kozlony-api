from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF

app = FastAPI()  # ✅ define app first!

@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        if not contents:
            return JSONResponse(status_code=400, content={"error": "Uploaded file is empty"})

        if not contents.startswith(b"%PDF"):
            return JSONResponse(status_code=400, content={"error": "Not a valid PDF format"})

        pdf = fitz.open(stream=contents, filetype="pdf")
        total_pages = pdf.page_count
        full_text = ""

        for page_num in range(total_pages):
            page = pdf.load_page(page_num)

            # First try plain text extraction
            text = page.get_text("text")

            # Fallback to blocks if empty
            if not text.strip():
                blocks = page.get_text("blocks")
                if blocks:
                    text = "\n".join([b[4] for b in blocks if isinstance(b, tuple) and len(b) > 4])

            if not text.strip():
                text = f"[NO TEXT FOUND ON PAGE {page_num + 1}]"

            full_text += text + "\n\n---PAGE BREAK---\n\n"

        return JSONResponse({
            "page_count": total_pages,
            "text_snippet": full_text[:2000] + "..." if len(full_text) > 2000 else full_text
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
