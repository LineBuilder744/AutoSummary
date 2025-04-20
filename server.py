from fastapi import FastAPI
import uvicorn

# Импортируем созданные нами модули с роутерами
from ai_prompts.generate import router as prompts_router
from ai_prompts.extract_text import router as text_extraction_router
from db.db_router import router as db_router

# Создаем экземпляр FastAPI
app = FastAPI(title="AI Summary", description="Makes summary from the text and generates tests of this summary for better learning")

# Подключаем роутеры к приложению
app.include_router(prompts_router)
app.include_router(text_extraction_router)
app.include_router(db_router)

@app.get("/")
async def root():
    return {
        "message": "AI API is running. Available endpoints:",
        "endpoints": [
            "/extract_text_png",
            "/generate_summary",
            "/generate_test",
            "/extract_text_from_pics",
            "/extract_text_from_pdf",
            "/summaries/(POST)",
            "/summaries/(GET)",
            "/summaries/(PUT)",
            "/summaries/[summary_id](DELETE)",
            "/summaries/[summary_id](GET)",
            "/summaries/subject/[subject_name]",
            "/summaries/title/[title]",

        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug") 