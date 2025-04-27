from fastapi import HTTPException, UploadFile, File, Form
from typing import List, Optional
# Switch back to absolute imports
from services.ai_services.ai_utils.utils import AIResponse
from services.ai_services.ai_utils.make_prompt import make_prompt
from services.ai_services.ai_utils.system_prompts import get_extract_text_png_sys_prompt, get_extract_png_summary_sys_prompt
from services.ai_services.extraction.formats.format_utils.format_utils import convert_pdf_to_images, get_png_payload

# Import router using absolute path
from services.ai_services.extraction.extraction_router import router

@router.post("/pdf", response_model=AIResponse)
async def extract_pdf(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    first_page: Optional[int] = Form(None),
    last_page: Optional[int] = Form(None),
    summarize: Optional[bool] = Form(False)
):
    # Проверка размера файла перед чтением
    if file.size and file.size > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="The PDF file is too big. Max size: 20MB"
        )
    system_prompt = get_extract_text_png_sys_prompt(language)
    if summarize:
        system_prompt = get_extract_png_summary_sys_prompt(language)
    try:
        # Чтение содержимого PDF файла
        pdf_bytes = await file.read()

        images = convert_pdf_to_images(pdf_bytes=pdf_bytes, first_page=first_page, last_page=last_page)

        # Используем обновленную функцию gemini_request с PDF payload
        return await make_prompt(
            system_prompt=system_prompt,
            contents=get_png_payload(prompt="Please extract text from these pictures.", images=images),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке PDF файла: {str(e)}"
        )

