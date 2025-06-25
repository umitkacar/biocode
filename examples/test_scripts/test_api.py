"""Simple API test without complex imports"""
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="BioCode API Test", version="0.2.0")

@app.get("/")
async def root():
    return {"message": "BioCode API is running!", "version": "0.2.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "biocode"}

if __name__ == "__main__":
    print("🧬 Starting BioCode API on http://localhost:8000")
    print("📚 Docs available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)