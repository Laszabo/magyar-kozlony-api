from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF

app = FastAPI()

@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        pdf = fitz.open(stream=contents, filetype="pdf")
        total_pages = pdf.page_count
        full_text = ""

        for page_num in range(total_pages):
            page = pdf.load_page(page_num)
            full_text += page.get_text()
            full_text += "\n\n---PAGE BREAK---\n\n"

        return JSONResponse({
            "page_count": total_pages,
            "text_snippet": full_text[:2000] + "...",  # preview only
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
