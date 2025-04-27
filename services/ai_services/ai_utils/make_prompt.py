# ai_prompts/gemini_prompts.py
import google.generativeai as genai
from fastapi import HTTPException
import traceback
from .utils import AIResponse, _create_generation_config, cast_response_to_dict
from .config import config
# Настройка клиента Gemini
try:
    genai.configure(api_key=config.get("api_token"))
except Exception as e:
    print(f"Ошибка конфигурации Gemini SDK: {e}")
    # Можно добавить обработку ошибки, если ключ не найден или невалиден

async def make_prompt(system_prompt: str, contents) -> AIResponse:
    try:
        model = genai.GenerativeModel(
            model_name=config["model"],
            system_instruction=system_prompt,
            generation_config=_create_generation_config()
        )

        response = await model.generate_content_async(contents)
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
        return AIResponse(
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