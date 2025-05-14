from fastapi import HTTPException, UploadFile, File, Form
from typing import List, Optional
import logging
import io

# Импорты с абсолютными путями
from services.ai_services.ai_utils.utils import AIResponse
from services.ai_services.ai_utils.openrouter_prompt import openrouter_prompt
from services.ai_services.ai_utils.system_prompts import get_extract_text_sys_prompt, get_extract_summary_sys_prompt
from services.ai_services.extraction.formats.format_utils.validators import validate_file, handle_extraction_error

# Импорт роутера с абсолютным путем
from services.ai_services.extraction.extraction_router import router

# Настройка логирования
logger = logging.getLogger(__name__)

@router.post("/txt", response_model=AIResponse)
async def extract_txt(
    files: List[UploadFile] = File(...),
    language: str = Form("auto"),
    summarize: Optional[bool] = Form(False)
):    
    try:
        # Валидация всех файлов
        for file in files:
            validate_file(file, "txt")
        
        # Выбор системного промпта в зависимости от параметра summarize

        if(summarize):
            system_prompt = get_summary_sys_prompt(language)
        
        # Чтение содержимого всех текстовых файлов
        text_contents = []
        for file in files:
            content = await file.read()
            try:
                # Пытаемся декодировать как UTF-8
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                # Если не получается, пробуем другие кодировки
                try:
                    text_content = content.decode('cp1251')  # Windows-1251 для кириллицы
                except UnicodeDecodeError:
                    # Если и это не работает, используем latin-1 (который всегда работает)
                    text_content = content.decode('latin-1')
            
            text_contents.append(text_content)
            
            # Сбрасываем указатель файла для возможного повторного использования
            await file.seek(0)
        
        logger.info(f"Обработка {len(text_contents)} текстовых файлов")
        
        # Объединяем содержимое всех файлов
        combined_text = "".join(text_contents)
        
        # Отправляем запрос на обработку
        if(summarize):
            return await openrouter_prompt(
            system_prompt=system_prompt,
            contents=[{"type": "text", "text": combined_text}],
            )
        return combined_text

    except HTTPException:
        # Пробрасываем HTTPException дальше
        raise
    except Exception as e:
        handle_extraction_error(e, "txt")