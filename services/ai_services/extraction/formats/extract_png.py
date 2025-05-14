
from fastapi import HTTPException, UploadFile, File, Form
from typing import List, Optional
import logging
# Switch back to absolute imports
from services.ai_services.ai_utils.utils import AIResponse
from services.ai_services.ai_utils.openrouter_prompt import openrouter_prompt
from services.ai_services.ai_utils.system_prompts import get_extract_png_summary_sys_prompt, get_extract_text_png_sys_prompt
from services.ai_services.extraction.formats.format_utils.format_utils import convert_uploadfile_to_pil_image, get_png_payload
from services.ai_services.extraction.formats.format_utils.validators import validate_file, handle_extraction_error

# Import router using absolute path
from services.ai_services.extraction.extraction_router import router

# Настройка логирования
logger = logging.getLogger(__name__)

@router.post("/png", response_model=AIResponse)
async def extract_png(
    files: List[str] = Form(...),
    language: str = Form("auto"),
    summarize: Optional[bool] = Form(False)
):    
    try:
        # Валидация всех файлов
        
        system_prompt = get_extract_text_png_sys_prompt(language)
        if summarize:
            system_prompt = get_extract_png_summary_sys_prompt(language)
        
        # Конвертируем все изображения в PIL.Image
        # Используем функцию для множественных изображений
        return await openrouter_prompt(
            system_prompt=system_prompt,
            contents=get_png_payload(
                prompt="Please extract text from these images.", 
                images_base64=files
            ),
        )
    except HTTPException:
        # Пробрасываем HTTPException дальше
        raise
    except Exception as e:
        handle_extraction_error(e, "png")

    

