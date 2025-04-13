from typing import Dict, Any, Optional, Union, List   
from PIL import Image
from pydantic import BaseModel
import google.generativeai as genai
from google.generativeai.types import GenerationConfig, AsyncGenerateContentResponse
from typing import List
from pdf2image import convert_from_bytes
from PIL import Image
import io

class AIRequest(BaseModel):
    text: str
    stream: bool = False
    additional_params: Optional[Dict[str, Any]] = None
    num_questions: int = 5
    language: str = "auto"


class AIResponse(BaseModel):
    response: str
    raw_response: Dict[str, Any]


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

def get_image_payload(prompt:str, image: Image.Image):
    contents: List[Union[str, Image.Image]] = [prompt, image]

    return contents

def get_multi_image_payload(prompt: str, images: List[Image.Image]) -> List[Union[str, Image.Image]]:
    contents = [prompt]
    contents.extend(images)
    return contents

def get_pdf_payload(prompt: str, pdf_bytes: bytes) -> list:
    contents = [prompt, pdf_bytes]
    
    return contents


def convert_pdf_to_images(
    pdf_bytes: bytes,
    dpi: int = 200,
    first_page: Optional[int] = None,
    last_page: Optional[int] = None,
    fmt: str = 'jpeg',
    thread_count: int = 4
) -> List[Image.Image]:
    try:
        images = convert_from_bytes(
            pdf_bytes,
            dpi=dpi,
            first_page=first_page,
            last_page=last_page,
            fmt=fmt,
            thread_count=thread_count,
            use_pdftocairo=True,
            transparent=False
        )
        
        # Конвертируем в RGB, если нужно (для JPEG)
        if fmt.lower() == 'jpeg':
            images = [image.convert('RGB') for image in images]
            
        return images
        
    except Exception as e:
        raise ValueError(f"Ошибка конвертации PDF: {str(e)}")
