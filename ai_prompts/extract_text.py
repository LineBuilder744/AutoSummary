from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import base64
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from ai_prompts.config import *
from ai_prompts.make_prompt import make_prompt, GeminiResponse
import logging
from PIL import Image
import io
from ai_prompts.utils import *

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class PDFTextResponse(BaseModel):
    text: str
    language: str
    raw_response: Optional[dict] = None

async def convert_uploadfile_to_pil_image(upload_file: UploadFile) -> Image.Image:
    # Чтение байтов из файла
    contents = await upload_file.read()
    # Создание объекта BytesIO из байтов
    image_stream = io.BytesIO(contents)

    pil_image = Image.open(image_stream)
    pil_image.load()
    
    return pil_image


@router.post("/extract_text_from_pics", response_model=GeminiResponse)
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
            contents=get_multi_image_payload(
                prompt="Please extract text from these images.", 
                images=pil_images
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing images: {str(e)}"
        )


@router.post("/extract_text_from_pdf", response_model=PDFTextResponse)
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
        response = await make_prompt(
            system_prompt=get_extract_text_png_sys_prompt(language),
            contents=get_multi_image_payload(prompt="Please extract text from these pictures.", images=images),
        )
        return PDFTextResponse(
            text=response.response,
            language=language,
            raw_response={"page_count": len(images)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке PDF файла: {str(e)}"
        )
    

