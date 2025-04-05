import pytesseract
from PIL import Image
import os
import logging
import tempfile
import base64
from extract_png.language_setup import setup_language, get_tessdata_path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Можно указать путь к исполняемому файлу Tesseract, если он не в PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Для Windows

# Указываем путь к директории с языковыми данными
tessdata_dir = get_tessdata_path()
if os.path.exists(tessdata_dir):
    os.environ['TESSDATA_PREFIX'] = tessdata_dir
    logger.info(f"TESSDATA_PREFIX set to: {tessdata_dir}")
else:
    logger.warning(f"Directory not found: {tessdata_dir}, TESSDATA_PREFIX not set")
    
# Добавляем функцию для проверки доступных языков
def check_available_languages():
    try:
        languages = pytesseract.get_languages(config='')
        logger.info(f"Available languages: {languages}")
        return languages
    except Exception as e:
        logger.error(f"Error checking available languages: {str(e)}")
        return []

# Проверяем доступные языки при импорте модуля
available_languages = check_available_languages()

def ensure_language_available(lang):
    """
    Убеждается, что языковой пакет доступен, и пытается установить его при необходимости
    
    Args:
        lang (str): Код языка (например 'eng', 'rus')
        
    Returns:
        bool: True если язык доступен или был успешно установлен
    """
    global available_languages
    
    if lang == 'eng' or lang in available_languages:
        return True
        
    logger.info(f"Language '{lang}' not found, attempting to install...")
    installed = setup_language(lang)
    
    if installed:
        # Обновляем список доступных языков
        available_languages = check_available_languages()
        return lang in available_languages
    
    return False

def extract_text_from_image(image_path, lang='eng'):
    """
    Извлекает текст из изображения используя Tesseract OCR.
    
    Args:
        image_path (str): Путь к файлу изображения
        lang (str): Язык для OCR (например 'eng', 'rus', 'eng+rus')
        
    Returns:
        str: Извлеченный текст
    """
    try:
        logger.info(f"Extracting text from image: {image_path}")
        
        # Проверяем, доступен ли указанный язык, и устанавливаем при необходимости
        if not ensure_language_available(lang):
            logger.warning(f"Language '{lang}' not available, falling back to 'eng'")
            lang = 'eng'
            
        # Проверяем существование файла
        if not os.path.exists(image_path):
            logger.error(f"File not found: {image_path}")
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Открываем изображение и применяем OCR
        image = Image.open(image_path)
        
        # Распознаем текст
        text = pytesseract.image_to_string(image, lang=lang)
        
        logger.info(f"Text extraction complete. Extracted {len(text)} characters")
        return text
    
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        raise

def extract_text_from_base64(base64_image, lang='eng'):
    """
    Извлекает текст из изображения, закодированного в base64.
    
    Args:
        base64_image (str): Строка с изображением в формате base64
        lang (str): Язык для OCR (например 'eng', 'rus', 'eng+rus')
        
    Returns:
        str: Извлеченный текст
    """
    try:
        logger.info("Extracting text from base64 image")
        
        # Проверяем, доступен ли указанный язык, и устанавливаем при необходимости
        if not ensure_language_available(lang):
            logger.warning(f"Language '{lang}' not available, falling back to 'eng'")
            lang = 'eng'
            
        # Декодируем base64 в бинарные данные
        image_data = base64.b64decode(base64_image)
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name
        
        try:
            # Обрабатываем изображение
            text = extract_text_from_image(temp_file_path, lang)
            return text
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Error extracting text from base64 image: {str(e)}")
        raise 