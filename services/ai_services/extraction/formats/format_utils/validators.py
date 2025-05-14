import logging
from fastapi import HTTPException, UploadFile
from typing import List, Optional, Dict, Any, Union

logger = logging.getLogger(__name__)

# Константы для размеров файлов (в МБ)
MAX_FILE_SIZE_MB = 20

# Константы для MIME-типов
ALLOWED_MIME_TYPES = {
    "png": ["image/png", "image/jpeg", "image/jpg"],
    "pdf": ["application/pdf"],
    "doc": [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx
        "application/msword",  # doc
        "application/vnd.ms-word"  # также doc
    ],
    "txt": ["text/plain"] 
}

def validate_file_size(file: UploadFile, max_size_mb: int = MAX_FILE_SIZE_MB) -> None:
    """
    Проверяет размер файла на соответствие ограничениям.
    
    Args:
        file: Файл для проверки
        max_size_mb: Максимальный размер файла в МБ
        
    Raises:
        HTTPException: Если файл превышает максимальный размер
    """
    if file.size and file.size > max_size_mb * 1024 * 1024:
        logger.warning(f"File {file.filename} exceeds size limit")
        raise HTTPException(
            status_code=400,
            detail=f"File {file.filename} is too big. Max size: {max_size_mb}MB"
        )

def validate_file_type(file: UploadFile, file_type: str) -> None:
    """
    Проверяет тип файла на соответствие разрешенным MIME-типам.
    
    Args:
        file: Файл для проверки
        file_type: Тип файла ('png', 'pdf', 'doc')
        
    Raises:
        HTTPException: Если тип файла не соответствует разрешенным
    """
    allowed_types = ALLOWED_MIME_TYPES.get(file_type, [])
    if not allowed_types:
        logger.error(f"Unknown file type category: {file_type}")
        raise ValueError(f"Unknown file type category: {file_type}")
        
    if file.content_type not in allowed_types:
        logger.warning(f"Invalid file type: {file.content_type} for file {file.filename}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed types: {', '.join(allowed_types)}"
        )

def validate_file(file: UploadFile, file_type: str, max_size_mb: int = MAX_FILE_SIZE_MB) -> None:
    """
    Выполняет полную валидацию файла (размер и тип).
    
    Args:
        file: Файл для проверки
        file_type: Тип файла ('png', 'pdf', 'doc')
        max_size_mb: Максимальный размер файла в МБ
        
    Raises:
        HTTPException: При ошибках валидации
    """
    validate_file_size(file, max_size_mb)
    validate_file_type(file, file_type)

def handle_extraction_error(e: Exception, file_type: str) -> None:
    """
    Обрабатывает ошибки, возникающие при извлечении данных из файлов.
    
    Args:
        e: Исключение
        file_type: Тип файла ('png', 'pdf', 'doc')
        
    Raises:
        HTTPException: С соответствующим сообщением об ошибке
    """
    if isinstance(e, ValueError):
        logger.error(f"Value error during {file_type} processing: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {file_type} format: {str(e)}"
        )
    elif isinstance(e, IOError):
        logger.error(f"IO error during {file_type} processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reading {file_type} file: {str(e)}"
        )
    else:
        logger.error(f"Unexpected error during {file_type} processing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing {file_type} file: {str(e)}"
        )