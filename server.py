from fastapi import FastAPI
import uvicorn

# Импортируем созданные нами модули с роутерами
from extract_png.routes import router as extract_png_router
from ai_prompts.prompts import router as prompts_router

# Создаем экземпляр FastAPI
app = FastAPI(title="AI Summary", description="Makes summary from the text and generates tests of this summary for better learning")

# Подключаем роутеры к приложению
app.include_router(extract_png_router)
app.include_router(prompts_router)

@app.get("/")
async def root():
    return {
        "message": "AI API is running. Available endpoints:",
        "endpoints": [
            "/extract_text_png",
            "/upload_and_extract",
            "/generate_summary",
            "/generate_test"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug") 