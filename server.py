from fastapi import FastAPI
import uvicorn

# Импортируем созданные нами модули с роутерами
from ai_prompts.generate import router as generate_router
from extract_png.routes import router as extract_png_router


# Создаем экземпляр FastAPI
app = FastAPI(title="DeepSeek AI API", description="API for interacting with DeepSeek AI")

# Подключаем роутеры к приложению
app.include_router(generate_router)
app.include_router(extract_png_router)


@app.get("/")
async def root():
    return {
        "message": "DeepSeek AI API is running. Available endpoints:",
        "endpoints": [
            "/generate",
            "/extract_text_png",
            "/upload_and_extract"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug") 