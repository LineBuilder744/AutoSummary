# Extract PNG - Модуль для извлечения текста из изображений

Модуль для извлечения текста из PNG и других изображений с использованием Tesseract OCR.

## Требования

- Python 3.7+
- Tesseract OCR 5.0+

### Установка Tesseract OCR

#### Windows

1. Скачайте установщик Tesseract для Windows с [официальной страницы](https://github.com/UB-Mannheim/tesseract/wiki)
2. Установите, выбрав опцию установки дополнительных языковых данных при необходимости
3. Убедитесь, что путь к Tesseract добавлен в переменную среды PATH (обычно `C:\Program Files\Tesseract-OCR`)

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install tesseract-ocr
# Для дополнительных языков:
sudo apt install tesseract-ocr-rus tesseract-ocr-deu # и другие необходимые языки
```

#### macOS

```bash
brew install tesseract
# Для дополнительных языков:
brew install tesseract-lang
```

## Интеграция с FastAPI сервером

Модуль интегрируется с FastAPI сервером и предоставляет следующие эндпоинты:

- `/extract_text_png` - извлечение текста из изображения по указанному пути или из base64-строки
- `/upload_and_extract` - загрузка изображения и извлечение текста
- `/available_languages` - получение списка доступных языковых пакетов
- `/install_language` - установка нового языкового пакета на сервере

## Автоматическая установка языковых пакетов

Модуль поддерживает автоматическую установку языковых пакетов для Tesseract OCR:

1. **Через API-запрос**: используйте POST запрос к `/install_language` с JSON `{"language": "rus"}` для установки русского языка
2. **Автоматически при использовании**: при указании языка, который еще не установлен, система попытается его установить

### Использование API

#### Извлечение текста из изображения по пути или из base64

```python
import requests
import json
import base64

# URL сервера
SERVER_URL = "http://localhost:8000"

# Извлечение текста из файла
response = requests.post(
    f"{SERVER_URL}/extract_text_png",
    json={
        "image_path": "/path/to/image.png",
        "language": "rus"  # Язык будет установлен автоматически, если отсутствует
    }
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# Извлечение текста из base64
with open("/path/to/image.png", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

response = requests.post(
    f"{SERVER_URL}/extract_text_png",
    json={
        "base64_image": encoded_image,
        "language": "eng+rus"  # Можно использовать комбинацию языков
    }
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

#### Загрузка изображения через форму

```python
import requests

# URL сервера
SERVER_URL = "http://localhost:8000"

# Загрузка файла и извлечение текста
with open("/path/to/image.png", "rb") as image_file:
    files = {"file": ("image.png", image_file, "image/png")}
    response = requests.post(
        f"{SERVER_URL}/upload_and_extract",
        files=files,
        data={"language": "rus"}
    )
    
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

#### Проверка доступных языков и установка новых

```python
import requests

# URL сервера
SERVER_URL = "http://localhost:8000"

# Получение списка доступных языков
response = requests.get(f"{SERVER_URL}/available_languages")
print("Доступные языки:", response.json()["available_languages"])

# Установка нового языкового пакета
response = requests.post(
    f"{SERVER_URL}/install_language",
    json={"language": "deu"}  # Установка немецкого языка
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

## Тестирование

Для тестирования извлечения текста можно использовать скрипт `test_extract_png.py`:

```bash
python test_extract_png.py --image_path "path/to/image.png" --language "rus" --method "all"
```

## Поддерживаемые языки

Модуль поддерживает все языки, доступные для Tesseract OCR. Некоторые распространенные коды языков:

- `eng` - английский (установлен по умолчанию)
- `rus` - русский
- `deu` - немецкий
- `fra` - французский
- `spa` - испанский
- `ita` - итальянский
- `chi_sim` - китайский (упрощенный)
- `jpn` - японский

Можно указать комбинацию языков, например `eng+rus` для лучшего распознавания текста на нескольких языках.

## Примечания

- Для наилучших результатов используйте изображения высокого качества с четким текстом
- Производительность OCR зависит от качества изображения, контраста текста и фона
- Если у вас возникают проблемы с распознаванием определенного языка, проверьте наличие соответствующего языкового пакета через API `/available_languages`
- Модуль автоматически установит недостающие языковые пакеты, если у пользователя есть соответствующие права
- В случае проблем с автоматической установкой языков, пользователь может установить их вручную, следуя инструкциям для своей ОС 