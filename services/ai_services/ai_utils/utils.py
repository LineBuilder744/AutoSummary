from typing import Dict, Any, Optional
from pydantic import BaseModel
from google.generativeai.types import GenerationConfig, AsyncGenerateContentResponse
from .config import config


class AIRequest(BaseModel):
    text: str
    stream: bool = False
    additional_params: Optional[Dict[str, Any]] = None
    num_questions: int = 5
    language: str = "auto"


class AIResponse(BaseModel):
    response: str
    raw_response: Dict[str, Any]

def _create_generation_config() -> GenerationConfig:
    
    return GenerationConfig(
        temperature=config["temperature"],
        top_p=config["top_p"],
        max_output_tokens=config["max_tokens"]
    )

def cast_response_to_dict(response: AsyncGenerateContentResponse) -> Dict[str, Any]:
    """Преобразует AsyncGenerateContentResponse в словарь."""
    result = {}
    
    # Базовые поля
    result["done"] = response._done
    result["iterator"] = str(response.iterator) if response._iterator else None
    
    # Обрабатываем result (GenerateContentResponse)
    if hasattr(response, 'result'):
        result["result"] = {
            "candidates": [],
            "usage_metadata": None,
            "model_version": getattr(response.result, "model_version", None)
        }
        
        # Обрабатываем кандидатов
        
        for candidate in response._result.candidates:
            candidate_dict = {
                "content": {
                    "parts": [],
                    "role": getattr(candidate.content, "role", None)
                },
                "finish_reason": str(candidate.finish_reason),
                "safety_ratings": [
                    {
                        "category": str(rating.category),
                        "probability": str(rating.probability)
                    } for rating in getattr(candidate, "safety_ratings", [])
                ]
            }
            
            # Обрабатываем части контента
            for part in candidate.content.parts:
                part_dict = {"text": part.text} if hasattr(part, "text") else {"data": str(part)}
                candidate_dict["content"]["parts"].append(part_dict)
            
            result["result"]["candidates"].append(candidate_dict)
        
        # Обрабатываем метаданные использования
        if hasattr(response.result, "usage_metadata"):
            result["result"]["usage_metadata"] = {
                "prompt_token_count": response.result.usage_metadata.prompt_token_count,
                "candidates_token_count": response.result.usage_metadata.candidates_token_count,
                "total_token_count": response.result.usage_metadata.total_token_count
            }
    
    return result