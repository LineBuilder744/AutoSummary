from fastapi import FastAPI
import uvicorn

# Импортируем созданные нами модули с роутерами
from generate import router as generate_router
from xml_routes import router as xml_router

# Создаем экземпляр FastAPI
app = FastAPI(title="DeepSeek AI API", description="API for interacting with DeepSeek AI")

# Подключаем роутеры к приложению
app.include_router(generate_router)
app.include_router(xml_router)

@app.get("/")
async def root():
    return {"message": "DeepSeek AI API is running. Available endpoints: /generate, /parse_xml, /create_summary_xml, /create_test_xml"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug") 