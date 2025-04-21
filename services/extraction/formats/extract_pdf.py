from fastapi import HTTPException, UploadFile, File, Form
from utils.utils import AIResponse
from utils.make_prompt import make_prompt
from format_utils.format_utils import convert_pdf_to_images, get_png_payload
from format_utils.extract_patterns import get_extract_text_png_sys_prompt

from extraction_router import router

@router.post("/pdf", response_model=AIResponse)
async def extract_text_from_pdf(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    first_page: Optional[int] = None,
    last_page: Optional[int] = None,
):
    # Проверка размера файла перед чтением
    if file.size and file.size > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="The PDF file is too big. Max size: 20MB"
        )
    
    try:
        # Чтение содержимого PDF файла
        pdf_bytes = await file.read()

        images = convert_pdf_to_images(pdf_bytes=pdf_bytes, first_page=first_page, last_page=last_page)

        # Используем обновленную функцию gemini_request с PDF payload
        return await make_prompt(
            system_prompt=get_extract_text_png_sys_prompt(language),
            contents=get_png_payload(prompt="Please extract text from these pictures.", images=images),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке PDF файла: {str(e)}"
        )