from fastapi import HTTPException, UploadFile, File, Form
from typing import List
from prompts.config import *
from prompts.utils import AIResponse
from prompts.make_prompt import make_prompt
from format_utils.extract_patterns import get_extract_text_png_sys_prompt
from format_utils.format_utils import convert_uploadfile_to_pil_image, get_png_payload

from extraction_router import router

@router.post("/png", response_model=AIResponse)
async def extract_text_from_multiple_pics(
    files: List[UploadFile] = File(...),
    language: str = Form("auto")
):    
    # Проверка размера каждого файла
    for file in files:
        if file.size and file.size > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Image {file.filename} is too big. Max size: 20MB"
            )
    
    try:
        # Конвертируем все изображения в PIL.Image
        pil_images = []
        for file in files:
            pil_image = await convert_uploadfile_to_pil_image(file)
            pil_images.append(pil_image)
        
        # Используем функцию для множественных изображений
        return await make_prompt(
            system_prompt=get_extract_text_png_sys_prompt(language),
            contents=get_png_payload(
                prompt="Please extract text from these images.", 
                images=pil_images
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing images: {str(e)}"
        )

    

