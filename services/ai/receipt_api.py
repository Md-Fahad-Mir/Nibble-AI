from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import shutil
import tempfile
import os

from offline import analyze, format_receipt_result

app = FastAPI(
    title="Receipt OCR API",
    description="Upload a receipt image and receive structured receipt data.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)


@app.get("/")
def root():
    return {
        "api": "Receipt OCR API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "parse_receipt": "/receipt (POST)",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/receipt")
async def parse_receipt(file: UploadFile = File(...), do_autocrop: bool = True):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    suffix = os.path.splitext(file.filename)[1].lower() or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        try:
            shutil.copyfileobj(file.file, tmp)
            tmp.flush()
            tmp_path = tmp.name
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to save upload: {exc}")

    try:
        items, discounts = analyze(tmp_path, do_autocrop=do_autocrop)
        result = format_receipt_result(items, discounts)
        return JSONResponse(content=result)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Uploaded file not found")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}")
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("receipt_api:app", host="0.0.0.0", port=8000, reload=True)
