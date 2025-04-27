from fastapi import HTTPException, UploadFile, File, Form
from typing import List, Optional
# Switch back to absolute imports
from services.ai_services.ai_utils.make_prompt import make_prompt
from services.ai_services.ai_utils.system_prompts import get_summary_sys_prompt
from services.ai_services.extraction.formats.format_utils.format_utils import get_text_from_docx
from services.ai_services.ai_utils.utils import AIResponse
from services.ai_services.extraction.extraction_router import router


@router.post("/doc", response_model=AIResponse)
async def extract_doc(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    summarize: Optional[bool] = Form(False)
):
    # Проверка размера файла перед чтением
    if file.size and file.size > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="The DOC/DOCX file is too big. Max size: 20MB"
        )
    
    try:
        # Чтение содержимого файла
        doc_bytes = await file.read() 

        result = get_text_from_docx(doc_bytes)

        if(summarize):
            return await make_prompt(
                system_prompt=get_summary_sys_prompt(language),
                contents=result)

        return AIResponse(
            response=result,
            raw_response={'response': result}
        )
        # Возвращаем результат в формате AIResponse с правильными полями
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке DOC/DOCX файла: {str(e)}"
        )

