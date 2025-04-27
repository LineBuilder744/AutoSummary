from fastapi import HTTPException, UploadFile, File, Form
from typing import List, Optional
import logging
# Switch back to absolute imports
from services.ai_services.ai_utils.utils import AIResponse
from services.ai_services.ai_utils.make_prompt import make_prompt
from services.ai_services.ai_utils.system_prompts import get_extract_text_png_sys_prompt, get_extract_png_summary_sys_prompt
from services.ai_services.extraction.formats.format_utils.format_utils import convert_pdf_to_images, get_png_payload
from services.ai_services.extraction.formats.format_utils.validators import validate_file, handle_extraction_error

# Import router using absolute path
from services.ai_services.extraction.extraction_router import router

# Настройка логирования
logger = logging.getLogger(__name__)

@router.post("/pdf", response_model=AIResponse)
async def extract_pdf(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    first_page: Optional[int] = Form(None),
    last_page: Optional[int] = Form(None),
    summarize: Optional[bool] = Form(False)
):
    try:
        # Валидация файла
        validate_file(file, "pdf")
        
        # Проверка логики номеров страниц
        if first_page is not None and last_page is not None and first_page > last_page:
            logger.warning(f"Invalid page range: first_page ({first_page}) > last_page ({last_page})")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid page range: first_page ({first_page}) cannot be greater than last_page ({last_page})"
            )
            
        system_prompt = get_extract_text_png_sys_prompt(language)
        if summarize:
            system_prompt = get_extract_png_summary_sys_prompt(language)
            
        # Чтение содержимого PDF файла
        pdf_bytes = await file.read()

        images = convert_pdf_to_images(pdf_bytes=pdf_bytes, first_page=first_page, last_page=last_page)

        logger.info(f"Processing PDF with {len(images)} extracted images")
        
        # Используем обновленную функцию gemini_request с PDF payload
        return await make_prompt(
            system_prompt=system_prompt,
            contents=get_png_payload(prompt="Please extract text from these pictures.", images=images),
        )
    except HTTPException:
        # Пробрасываем HTTPException дальше
        raise
    except Exception as e:
        handle_extraction_error(e, "pdf")

