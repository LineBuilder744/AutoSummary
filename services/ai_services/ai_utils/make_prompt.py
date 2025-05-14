# ai_prompts/gemini_prompts.py
import google.generativeai as genai
from google.generativeai.types import GenerationConfig 
from fastapi import HTTPException
import traceback
from .utils import AIResponse, cast_response_to_dict
from dotenv import load_dotenv
import os

load_dotenv()
# Настройка клиента Gemin
# Fix the API key configuration
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Use os.getenv instead of config.get
except Exception as e:
    print(f"Ошибка конфигурации Gemini SDK: {e}")

async def make_prompt(system_prompt: str, contents) -> AIResponse:
    try:
        model = genai.GenerativeModel(
            model_name=os.getenv("MODEL"),
            system_instruction=system_prompt,
            generation_config=GenerationConfig(
                temperature=float(os.getenv("TEMPERATURE")),
                top_p=float(os.getenv("TOP_P")),
                max_output_tokens=int(os.getenv("MAX_TOKENS")),  # Fix typo: ax_output_tokens → max_output_tokens
            )
        )

        response = await model.generate_content_async(contents)
        response_text = response.text  # Extract text from response

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