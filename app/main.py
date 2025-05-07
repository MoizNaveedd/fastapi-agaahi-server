import uvicorn
from fastapi import FastAPI
from app.config import settings
from app.services.query_service import router as query_router

app = FastAPI(title="SQL Chat API")

# Include routers
app.include_router(query_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to SQL Chat API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 