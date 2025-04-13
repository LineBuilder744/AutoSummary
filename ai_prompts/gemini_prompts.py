# ai_prompts/gemini_prompts.py
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import traceback
from ai_prompts.utils import *
# Импортируем конфигурацию
try:
    from .config import config
except ImportError:
    # Если запуск как скрипт, пробуем абсолютный импорт
    from config import config

# Настройка клиента Gemini
try:
    genai.configure(api_key=config.get("api_token"))
except Exception as e:
    print(f"Ошибка конфигурации Gemini SDK: {e}")
    # Можно добавить обработку ошибки, если ключ не найден или невалиден

# Определяем модель ответа, совместимую с FastAPI
class GeminiResponse(BaseModel):
    response: str
    raw_response: Optional[Dict[str, Any]] = None

def _create_generation_config() -> GenerationConfig:
    
    return GenerationConfig(
        temperature=config["temperature"],
        top_p=config["top_p"],
        max_output_tokens=config["max_tokens"]
    )

async def gemini_request(system_prompt: str, contents) -> GeminiResponse:
    try:
        model = genai.GenerativeModel(
            model_name=config["model"],
            system_instruction=system_prompt,
            generation_config=_create_generation_config()
        )

        response = await model.generate_content_async(contents)

        print(response)
        # Извлекаем текст из ответа, обрабатываем возможные ошибки
        try:
            response_text = response.text
        except ValueError as e:
            # Обработка случая, когда text недоступен из-за copyright или других причин
            if "finish_reason" in str(e) and "4" in str(e):
                response_text = "Не удалось обработать данный контент из-за возможных проблем с авторскими правами."
            else:
                response_text = f"Не удалось получить текст из ответа: {str(e)}"
        
        # Возвращаем GeminiResponse с текстом и сырым ответом
        return GeminiResponse(
            response=response_text,
            raw_response=cast_response_to_dict(response=response)
        )

    except Exception as e:
        print(f"Ошибка при запросе к Gemini API: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка взаимодействия с Gemini API: {str(e)}"
        )