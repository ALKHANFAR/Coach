"""اختبار بسيط للنظام"""
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Test App")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/healthz")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
