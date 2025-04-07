import requests
import os

def generate_summary(text):

    server_url="http://localhost:8000"
    # Prepare the API request
    endpoint = f"{server_url}/generate_summary"
    
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    payload = {
        "text": text,
    }
    
    try:
        # Send the request to the server
        response = requests.post(endpoint, json=payload, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            return result["response"]
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def generate_test(summary, num_questions=5):


    server_url = 'http://localhost:8000'
    
    # Prepare the API request
    endpoint = f"{server_url}/generate_test"
    
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    # Prepare payload
    payload = {
        "text": summary,
        "num_questions": num_questions
    }
    
    try:
        # Send the request to the server
        response = requests.post(endpoint, json=payload, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            return result["response"]
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def extract_summary(response):
    # Find the <summary> tag
    start_idx = response.find("<summary>")
    end_idx = response.find("</summary>", start_idx) + len("</summary>")
    
    if start_idx != -1 and end_idx != -1:
        return response[start_idx:end_idx]
    
    # Return the full response if we can't extract the summary
    return response

def png_to_text(image_path: str, language: str = "auto"):
    """
    Отправляет изображение на сервер для извлечения текста.
    
    Args:
        image_path (str): Путь к файлу изображения
        language (str): Язык текста в изображении (по умолчанию "auto")
        
    Returns:
        dict: Ответ сервера с извлеченным текстом
    """
    server_url = 'http://localhost:8000'
    endpoint = f"{server_url}/extract_text_from_pic"

    try:
        # Проверяем существование файла
        if not os.path.exists(image_path):
            print(f"Ошибка: Файл не найден: {image_path}")
            return {"error": "File not found"}
            
        # Открываем файл для отправки
        with open(image_path, "rb") as image_file:
            # Создаем multipart/form-data запрос
            files = {"file": (os.path.basename(image_path), image_file, "image/jpeg")}
            data = {"language": language}
            
            # Отправляем запрос на сервер
            response = requests.post(endpoint, files=files, data=data)
        
        # Проверяем ответ
        if response.status_code == 200:
            result = response.json()
            print(f"Текст успешно извлечен из изображения")
            print(f"Количество символов: {len(result.get('text', ''))}")
            return result
        else:
            print(f"Ошибка: {response.status_code}")
            print(response.text)
            return {"error": f"Server returned status code {response.status_code}"}
            
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return {"error": str(e)}

def extract_test(response):
    """
    Extracts the test XML from the response
    
    Args:
        response (str): The response from the API
        
    Returns:
        str: The extracted test
    """
    # Find the <test> tag
    start_idx = response.find("<test>")
    end_idx = response.find("</test>", start_idx) + len("</test>")
    
    if start_idx != -1 and end_idx != -1:
        return response[start_idx:end_idx]
    
    # Return the full response if we can't extract the test
    return response

def main():

    what_to_generate = input("What do you need? (summary/test/png): ")

    # Если пользователь выбрал извлечение текста из изображения
    if what_to_generate.lower() == "png":
        image_path = input("Введите путь к изображению: ")
        language = input("Введите язык текста (оставьте пустым для auto): ") or "auto"
        
        print("\nИзвлечение текста из изображения, пожалуйста, подождите...")
        result = png_to_text(image_path, language)
        
        if result and "error" not in result:
            extracted_text = result.get("text", "")
            print("\n--- Извлеченный текст ---\n")
            print(extracted_text)
            
            # Сохраняем в файл
            output_file = "extracted_text.txt"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(extracted_text)
                print(f"\nТекст сохранен в файл {output_file}")
            except Exception as e:
                print(f"Ошибка при сохранении текста: {str(e)}")
                
            # Спрашиваем, хочет ли пользователь сгенерировать summary из этого текста
            generate_summary_prompt = input("\nХотите создать конспект из этого текста? (да/нет): ")
            if generate_summary_prompt.lower() in ["да", "yes", "y", "д"]:
                print("\nГенерация конспекта, пожалуйста, подождите...")
                summary_response = generate_summary(extracted_text)
                
                if summary_response:
                    summary = extract_summary(summary_response)
                    print("\n--- Сгенерированный конспект ---\n")
                    print(summary)
                    
                    # Сохраняем в файл
                    output_file = "summary_output.xml"
                    try:
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(summary)
                        print(f"\nКонспект сохранен в файл {output_file}")
                    except Exception as e:
                        print(f"Ошибка при сохранении конспекта: {str(e)}")
        return
        
    # Get text from file or user input
    text = open("text.txt", "r").read()
    summary = open("summary.txt", "r").read()

    # Process based on user choice
    if what_to_generate.lower() == "summary":
        print("\nGenerating summary, please wait...")
        summary_response = generate_summary(text)
        
        if summary_response:
            summary = extract_summary(summary_response)
            print("\n--- Generated Summary ---\n")
            print(summary)
            
            # Save to file
            output_file = "summary_output.xml"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(summary)
                print(f"\nSummary saved to {output_file}")
            except Exception as e:
                print(f"Error saving summary: {str(e)}")
                
            # Ask if user wants to generate a test from this summary
            generate_test_prompt = input("\nDo you want to generate a test from this summary? (yes/no): ")
            if generate_test_prompt.lower() in ["yes", "y"]:
                what_to_generate = "test"
                # Continue to test generation
    
    if what_to_generate.lower() == "test":
        # If we don't have a summary yet, we need to generate one first
        print(f"\nGenerating test with {5} questions, please wait...")
        test_response = generate_test(summary)
        
        if test_response:
            test = extract_test(test_response)
            print("\n--- Generated Test ---\n")
            print(test)
            
            # Save to file
            output_file = "test_output.xml"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(test)
                print(f"\nTest saved to {output_file}")
            except Exception as e:
                print(f"Error saving test: {str(e)}")
    elif what_to_generate.lower() not in ["summary", "test"]:
        print("Invalid option. Please choose 'summary' or 'test'.")

if __name__ == "__main__":
    main() 