import os
import sys
import urllib.request
import platform
import subprocess
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# URL для скачивания языковых файлов
TESSDATA_URL = "https://github.com/tesseract-ocr/tessdata/raw/main/{}.traineddata"

def get_tessdata_path():
    """Определяет путь к директории tessdata"""
    # Для Windows
    if platform.system() == "Windows":
        # Стандартные пути установки Tesseract
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tessdata",
            r"C:\Program Files (x86)\Tesseract-OCR\tessdata"
        ]
        
        # Проверяем переменную окружения
        if 'TESSDATA_PREFIX' in os.environ:
            possible_paths.insert(0, os.environ['TESSDATA_PREFIX'])
            
        # Ищем первый существующий путь
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        # Если не нашли, используем путь по умолчанию
        default_path = r"C:\Program Files\Tesseract-OCR\tessdata"
        os.makedirs(default_path, exist_ok=True)
        return default_path
        
    # Для Linux и macOS
    else:
        # Стандартные пути установки
        possible_paths = [
            "/usr/share/tesseract-ocr/4.00/tessdata",
            "/usr/share/tesseract-ocr/tessdata",
            "/usr/local/share/tessdata",
            "/opt/homebrew/share/tessdata",  # Для macOS с Homebrew
        ]
        
        # Проверяем переменную окружения
        if 'TESSDATA_PREFIX' in os.environ:
            possible_paths.insert(0, os.environ['TESSDATA_PREFIX'])
            
        # Ищем первый существующий путь
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        # Если не нашли, используем путь пользователя
        user_path = os.path.expanduser("~/.local/share/tessdata")
        os.makedirs(user_path, exist_ok=True)
        return user_path

def download_language_file(lang_code):
    """Скачивает языковой файл по коду языка"""
    tessdata_path = get_tessdata_path()
    lang_file_path = os.path.join(tessdata_path, f"{lang_code}.traineddata")
    
    # Проверяем, существует ли уже файл
    if os.path.exists(lang_file_path):
        logger.info(f"Language file for '{lang_code}' already exists at {lang_file_path}")
        return True
        
    # Скачиваем файл
    url = TESSDATA_URL.format(lang_code)
    try:
        logger.info(f"Downloading language file for '{lang_code}' from {url}")
        urllib.request.urlretrieve(url, lang_file_path)
        logger.info(f"Successfully downloaded language file to {lang_file_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading language file: {str(e)}")
        return False

def install_language_package(lang_code):
    """Устанавливает языковой пакет через системные пакетные менеджеры"""
    system = platform.system().lower()
    
    if system == "linux":
        try:
            logger.info(f"Attempting to install tesseract-ocr-{lang_code} package...")
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", f"tesseract-ocr-{lang_code}"], check=True)
            return True
        except Exception as e:
            logger.error(f"Error installing language package: {str(e)}")
            return False
    
    elif system == "darwin":  # macOS
        try:
            logger.info("Attempting to install tesseract-lang package...")
            subprocess.run(["brew", "install", "tesseract-lang"], check=True)
            return True
        except Exception as e:
            logger.error(f"Error installing language package: {str(e)}")
            return False
    
    # Для Windows используем скачивание напрямую
    return download_language_file(lang_code)

def setup_language(lang_code):
    """Настраивает языковой пакет для Tesseract"""
    # Если язык английский, он должен быть установлен по умолчанию
    if lang_code == "eng":
        return True
        
    # Для комбинации языков, обрабатываем каждый отдельно
    if "+" in lang_code:
        langs = lang_code.split("+")
        results = [setup_language(lang) for lang in langs]
        return all(results)
    
    # Пробуем сначала скачать файл напрямую
    if download_language_file(lang_code):
        return True
        
    # Если скачивание не удалось, пробуем через пакетный менеджер
    return install_language_package(lang_code)

if __name__ == "__main__":
    # Если скрипт запущен напрямую, устанавливаем язык из аргументов
    if len(sys.argv) > 1:
        lang_code = sys.argv[1]
        logger.info(f"Setting up language: {lang_code}")
        if setup_language(lang_code):
            logger.info(f"Language {lang_code} setup completed successfully")
        else:
            logger.error(f"Failed to setup language {lang_code}")
    else:
        logger.info("No language code provided. Usage: python language_setup.py [lang_code]")
        logger.info("Example: python language_setup.py rus")
        logger.info("Available languages: eng, rus, deu, fra, spa, ita, por, ara, hin, jpn, kor, chi_sim, chi_tra, etc.") 