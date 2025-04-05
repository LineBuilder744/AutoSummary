from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import logging
import os
import tempfile
from datetime import datetime
import time

from extract_png.extract_text import extract_text_from_image, extract_text_from_base64, check_available_languages
from extract_png.language_setup import setup_language

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Извлечение текста"])

class ExtractTextRequest(BaseModel):
    image_path: Optional[str] = None
    base64_image: Optional[str] = None
    language: str = "eng"

class ExtractTextResponse(BaseModel):
    text: str
    characters: int
    language: str
    source_type: str
    processing_time: float

class LanguageInstallRequest(BaseModel):
    language: str

class LanguageInstallResponse(BaseModel):
    success: bool
    message: str
    available_languages: list

@router.post("/extract_text_png")
async def extract_text_png(request: ExtractTextRequest):
    """
    Извлекает текст из PNG изображения.
    
    - **image_path**: Путь к файлу изображения на сервере (опционально)
    - **base64_image**: Изображение в формате base64 (опционально)
    - **language**: Язык для OCR (по умолчанию 'eng')
    """
    logger.info(f"Received request to extract text with language: {request.language}")
    
    start_time = time.time()
    
    # Проверяем, указан ли источник изображения
    if not request.image_path and not request.base64_image:
        raise HTTPException(status_code=400, detail="Either image_path or base64_image must be provided")
    
    try:
        # Извлекаем текст из указанного источника
        if request.image_path:
            text = extract_text_from_image(request.image_path, lang=request.language)
            source_type = "file_path"
        else:
            text = extract_text_from_base64(request.base64_image, lang=request.language)
            source_type = "base64"
        
        # Формируем ответ
        response = ExtractTextResponse(
            text=text,
            characters=len(text),
            language=request.language,
            source_type=source_type,
            processing_time=time.time() - start_time
        )
        
        logger.info(f"Text extraction completed. Extracted {len(text)} characters")
        return response
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")

@router.post("/upload_and_extract")
async def upload_and_extract(
    file: UploadFile = File(...),
    language: str = Form("eng")
):
    """
    Загружает изображение и извлекает из него текст.
    
    - **file**: Файл изображения для загрузки
    - **language**: Язык для OCR (по умолчанию 'eng')
    """
    logger.info(f"Received file upload: {file.filename}, language: {language}")
    start_time = time.time()
    
    try:
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            # Сохраняем загруженный файл
            contents = await file.read()
            temp_file.write(contents)
        
        try:
            # Извлекаем текст из файла
            text = extract_text_from_image(temp_file_path, lang=language)
            
            # Формируем ответ
            response = ExtractTextResponse(
                text=text,
                characters=len(text),
                language=language,
                source_type="uploaded_file",
                processing_time=time.time() - start_time
            )
            
            logger.info(f"Text extraction from uploaded file completed. Extracted {len(text)} characters")
            return response
        
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.debug(f"Temporary file removed: {temp_file_path}")
    
    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {str(e)}")

@router.get("/available_languages")
async def get_available_languages():
    """
    Возвращает список доступных языков для OCR
    """
    languages = check_available_languages()
    return {"available_languages": languages}

@router.post("/install_language")
async def install_language(request: LanguageInstallRequest, background_tasks: BackgroundTasks):
    """
    Устанавливает языковой пакет для указанного языка
    
    - **language**: Код языка для установки (например 'rus', 'deu')
    """
    logger.info(f"Received request to install language: {request.language}")
    
    try:
        # Проверяем наличие языка в уже установленных
        languages = check_available_languages()
        if request.language in languages:
            return LanguageInstallResponse(
                success=True,
                message=f"Language '{request.language}' is already installed",
                available_languages=languages
            )
        
        # Выполняем установку языкового пакета
        success = setup_language(request.language)
        
        # Обновляем список доступных языков
        updated_languages = check_available_languages()
        
        if success:
            message = f"Language '{request.language}' installed successfully"
        else:
            message = f"Failed to install language '{request.language}'"
        
        return LanguageInstallResponse(
            success=success,
            message=message,
            available_languages=updated_languages
        )
    
    except Exception as e:
        logger.error(f"Error installing language: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to install language: {str(e)}") 