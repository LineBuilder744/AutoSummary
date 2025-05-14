from fastapi import HTTPException, UploadFile, File, Form
from typing import List, Optional
import logging
# Switch back to absolute imports
from services.ai_services.ai_utils.openrouter_prompt import openrouter_prompt
from services.ai_services.ai_utils.system_prompts import get_summary_sys_prompt
from services.ai_services.extraction.formats.format_utils.format_utils import get_text_from_docx
from services.ai_services.ai_utils.utils import AIResponse
from services.ai_services.extraction.extraction_router import router
from services.ai_services.extraction.formats.format_utils.validators import validate_file, handle_extraction_error

# Настройка логирования
logger = logging.getLogger(__name__)

@router.post("/doc", response_model=AIResponse)
async def extract_doc(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    summarize: Optional[bool] = Form(False)
):
    try:
        # Валидация файла
        validate_file(file, "doc")
        
        # Чтение содержимого файла
        doc_bytes = await file.read() 

        result = get_text_from_docx(doc_bytes)

        if(summarize):
            return await openrouter_prompt(
                system_prompt=get_summary_sys_prompt(language),
                contents=result)

        return AIResponse(
            response=result,
            raw_response={'response': result}
        )
        
    except HTTPException:
        # Пробрасываем HTTPException дальше
        raise
    except Exception as e:
        handle_extraction_error(e, "doc")

