from fastapi import FastAPI
import uvicorn

# Импортируем созданные нами модули с роутерами
from services.ai_services.generation.generate_router import router as generate_router
from services.ai_services.extraction.extraction_router import router as extract_router

# Создаем экземпляр FastAPI
app = FastAPI(title="AI Summary", description="Makes summary from the text and generates tests of this summary for better learning")

# Подключаем роутеры к приложению
app.include_router(extract_router)
app.include_router(generate_router)

@app.get("/")
async def root():
    return {
        "message": "AI API is running. Available endpoints:",
        "endpoints": [
            "/extract/png",
            "/extract/pdf",
            "/extract/doc",
            "/extract/txt",
            "/generate/summary",
            "/generate/test",

        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug") 