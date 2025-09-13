from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Language Learning API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Language Learning API is running"}

@app.post("/api/extract-content")
async def extract_content(video_data: dict):
    # Placeholder for AI processing logic
    # This will extract vocabulary and grammar from video content
    return JSONResponse({
        "vocabulary": [
            {"word": "hello", "definition": "a greeting", "level": "A1"},
            {"word": "world", "definition": "the earth", "level": "A1"}
        ],
        "grammar": [
            {"concept": "Present Simple", "explanation": "Used for facts and habits", "level": "A1"}
        ]
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)