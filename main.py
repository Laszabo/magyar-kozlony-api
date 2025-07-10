from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pymupdf4llm

app = FastAPI()

@app.post("/chunk")
async def chunk_pdf(file: UploadFile = File(...)):
    # Read the uploaded file content
    contents = await file.read()

    try:
        # Save the uploaded PDF to memory or temporary path
        with open("temp.pdf", "wb") as temp_file:
            temp_file.write(contents)

        # Chunk the PDF using pymupdf4llm
        chunks = pymupdf4llm.to_markdown("temp.pdf", page_chunks=True)

        # Group chunks into 40-page blocks
        chunk_size = 40
        final_chunks = []

        for i in range(0, len(chunks), chunk_size):
            chunk_group = chunks[i:i + chunk_size]
            merged_text = "\n\n".join([c["text"] for c in chunk_group])

            final_chunks.append({
                "chunk_id": f"chunk_{(i // chunk_size) + 1:03}",
                "start_page": i + 1,
                "end_page": i + len(chunk_group),
                "text": merged_text.strip(),
                "tokens_estimate": int(len(merged_text.split()) * 1.3)
            })

        # Remove empty chunks
        final_chunks = [chunk for chunk in final_chunks if chunk['text'].strip()]

        return JSONResponse(content={
            "document_title": file.filename,
            "total_chunks": len(final_chunks),
            "chunks": final_chunks
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
