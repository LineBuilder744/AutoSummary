#!/usr/bin/env python3
import base64
import os
import requests

def test_extract_from_path(server_url, image_path, language="eng"):
    """
    Тестирует извлечение текста из изображения по указанному пути
    """
    print(f"\n--- Тестирование извлечения текста из файла {image_path} ---")
    
    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            print(f"ОШИБКА: Файл не найден: {image_path}")
            return False
        
        # Отправляем запрос к серверу
        response = requests.post(
            f"{server_url}/extract_text_png",
            json={
                "image_path": image_path,
                "language": language
            }
        )
        
        # Проверяем ответ
        if response.status_code != 200:
            print(f"ОШИБКА: Сервер вернул код {response.status_code}")
            print(response.text)
            return False
        
        # Выводим результат
        result = response.json()
        print(f"Язык: {result.get('language', 'не указан')}")
        print(f"Источник: {result.get('source_type', 'не указан')}")
        print(f"Количество символов: {result.get('characters', 0)}")
        print(f"Время обработки: {result.get('processing_time', 0):.2f} сек.")
        print("\nИзвлеченный текст:")
        print("-" * 50)
        print(result.get("text", "Текст не найден"))
        print("-" * 50)
        
        return True
    
    except Exception as e:
        print(f"ОШИБКА: {str(e)}")
        return False

def test_extract_from_base64(server_url, image_path, language="eng"):
    """
    Тестирует извлечение текста из изображения в формате base64
    """
    print(f"\n--- Тестирование извлечения текста из base64 (файл {image_path}) ---")
    
    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            print(f"ОШИБКА: Файл не найден: {image_path}")
            return False
        
        # Читаем и кодируем изображение
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Отправляем запрос к серверу
        response = requests.post(
            f"{server_url}/extract_text_png",
            json={
                "base64_image": encoded_image,
                "language": language
            }
        )
        
        # Проверяем ответ
        if response.status_code != 200:
            print(f"ОШИБКА: Сервер вернул код {response.status_code}")
            print(response.text)
            return False
        
        # Выводим результат
        result = response.json()
        print(f"Язык: {result.get('language', 'не указан')}")
        print(f"Источник: {result.get('source_type', 'не указан')}")
        print(f"Количество символов: {result.get('characters', 0)}")
        print(f"Время обработки: {result.get('processing_time', 0):.2f} сек.")
        print("\nИзвлеченный текст:")
        print("-" * 50)
        print(result.get("text", "Текст не найден"))
        print("-" * 50)
        
        return True
    
    except Exception as e:
        print(f"ОШИБКА: {str(e)}")
        return False

def test_upload_and_extract(server_url, image_path, language="eng"):
    """
    Тестирует загрузку изображения и извлечение текста из него
    """
    print(f"\n--- Тестирование загрузки и извлечения текста из файла {image_path} ---")
    
    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            print(f"ОШИБКА: Файл не найден: {image_path}")
            return False
        
        # Отправляем файл на сервер
        with open(image_path, "rb") as image_file:
            response = requests.post(
                f"{server_url}/upload_and_extract",
                files={"file": (os.path.basename(image_path), image_file)},
                data={"language": language}
            )
        
        # Проверяем ответ
        if response.status_code != 200:
            print(f"ОШИБКА: Сервер вернул код {response.status_code}")
            print(response.text)
            return False
        
        # Выводим результат
        result = response.json()
        print(f"Язык: {result.get('language', 'не указан')}")
        print(f"Источник: {result.get('source_type', 'не указан')}")
        print(f"Количество символов: {result.get('characters', 0)}")
        print(f"Время обработки: {result.get('processing_time', 0):.2f} сек.")
        print("\nИзвлеченный текст:")
        print("-" * 50)
        print(result.get("text", "Текст не найден"))
        print("-" * 50)
        
        return True
    
    except Exception as e:
        print(f"ОШИБКА: {str(e)}")
        return False

def check_available_languages(server_url):
    """
    Проверяет доступные языки на сервере
    """
    print("\n--- Проверка доступных языков ---")
    
    try:
        response = requests.get(f"{server_url}/available_languages")
        
        if response.status_code != 200:
            print(f"ОШИБКА: Сервер вернул код {response.status_code}")
            print(response.text)
            return False
        
        languages = response.json().get("available_languages", [])
        print("Доступные языки:")
        if languages:
            for lang in languages:
                print(f"- {lang}")
        else:
            print("Языковые пакеты не найдены")
        
        return True
    
    except Exception as e:
        print(f"ОШИБКА: {str(e)}")
        return False

def install_language(server_url, language):
    """
    Устанавливает языковой пакет на сервере
    """
    print(f"\n--- Установка языкового пакета: {language} ---")
    
    try:
        response = requests.post(
            f"{server_url}/install_language",
            json={"language": language}
        )
        
        if response.status_code != 200:
            print(f"ОШИБКА: Сервер вернул код {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        print(f"Успех: {result.get('success', False)}")
        print(f"Сообщение: {result.get('message', 'Нет сообщения')}")
        
        languages = result.get("available_languages", [])
        print("Доступные языки:")
        if languages:
            for lang in languages:
                print(f"- {lang}")
        else:
            print("Языковые пакеты не найдены")
        
        return result.get('success', False)
    
    except Exception as e:
        print(f"ОШИБКА: {str(e)}")
        return False

def main():
    # Настройка парсера аргументов
    # Тестирование извлечения текста различными методами
    
    test_extract_from_path("http://localhost:8000", "test_client_logic/88ss.png", "eng")
    

if __name__ == "__main__":
    main() 