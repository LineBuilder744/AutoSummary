from nt import system
from fastapi import HTTPException, UploadFile, File, Form
from typing import List, Optional
# Switch back to absolute imports
from services.ai_services.ai_utils.utils import AIResponse
from services.ai_services.ai_utils.make_prompt import make_prompt
from services.ai_services.ai_utils.system_prompts import get_extract_png_summary_sys_prompt, get_extract_text_png_sys_prompt
from services.ai_services.extraction.formats.format_utils.format_utils import convert_uploadfile_to_pil_image, get_png_payload

# Import router using absolute path
from services.ai_services.extraction.extraction_router import router

@router.post("/png", response_model=AIResponse)
async def extract_png(
    files: List[UploadFile] = File(...),
    language: str = Form("auto"),
    summarize: Optional[bool] = Form(False)
):    
    # Проверка размера каждого файла
    for file in files:
        if file.size and file.size > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Image {file.filename} is too big. Max size: 20MB"
            )

    system_prompt = get_extract_text_png_sys_prompt(language)
    if summarize:
        system_prompt = get_extract_png_summary_sys_prompt(language)
    
    try:
        # Конвертируем все изображения в PIL.Image
        pil_images = []
        for file in files:
            pil_image = await convert_uploadfile_to_pil_image(file)
            pil_images.append(pil_image)
        
        # Используем функцию для множественных изображений
        return await make_prompt(
            system_prompt=system_prompt,
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

    

