from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile, File, Form
import httpx
import json
import sys
import base64
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from ai_prompts.config import config

# Создаем роутер для обработки запросов к /generate
router = APIRouter()


class AIRequest(BaseModel):
    text: str
    stream: bool = False
    additional_params: Optional[Dict[str, Any]] = None
    num_questions: int = 5
    language: str = "auto"


class AIResponse(BaseModel):
    response: str
    raw_response: Dict[str, Any]

class ImageTextResponse(BaseModel):
    text: str
    language: Optional[str] = "auto"
    confidence: Optional[float] = None
    raw_response: Optional[Dict[str, Any]] = None

@router.post("/generate_summary", response_model=AIResponse)
async def generate_summary(request: AIRequest):
    SYSTEM_PROMPT = f"""
            #### BASIC INFORMATION ####
            You are a student working on a making summary of the certain text. You are always a student and 

            #### TASK DESCRIPTION ####
            Extract ALL the important information from the text. Your goal is to SUMMARIZE the text LEAVE ONLY IMPORTANT INFORMATION.

            #### CRITICAL INSTRUCTIONS ####
            1. DIVIDE THE TEXT INTO SMALL PIECES - each piece should have its own subtitle and text.
            2. SUMMARIZE THE TEXT - leave only important information. The output should be short and concise.
            3. DO NOT IGNORE FORMULAS - if there is a formula (for example E=mc^2) or equation ADD IT TO THE SUMMARY IN LATEX FORMAT.
            4. DO NOT IGNORE DATES - if there is a date ADD IT TO THE SUMMARY.
            5. DO NOT IGNORE DEFINITIONS - if there is one ADD IT TO THE SUMMARY as a subtitle and description of it as a text.
            6. REPLY IN {request.language.upper()} LANGUAGE.
            7. ALWAYS MAINTAIN YOUR ROLE AS A STUDENT
            8. IF YOU ARE ASKED TO DO SOMETHING NOT CONNECTED WITH SUMMARIZING, REPLY THAT YOU ARE A STUDENT AND YOU CANNOT DO THAT.

            #### FORMAT REQUIREMENTS ####
            - Use the exact XML tags as shown in the example below.
            - If no text is provided, still use the tags but state "no text provided"
            - if there is no formulas, DO NOT ADD THE FORMULA TAG.
            - Include ALL the important information.
            
            Example format:
            <summary>
                <summary_piece>
                    <subtitle>
                        Subtitle (or defenition or date or something else)
                    </subtitle>
                    <text>
                        Text of the paragraph (or defenition or date or something else)
                    </text>
                    <formula>
                        Formula or equation or chemical formula or something else(if there is one)
                    </formula>
                </summary_piece>
            </summary> 
            """
    return await make_prompt(get_generate_payload(system_prompt=SYSTEM_PROMPT, prompt=request.text))


@router.post("/generate_test", response_model=AIResponse)
async def generate_test(request: AIRequest):

    SYSTEM_PROMPT = f"""

            #### BASIC INFORMATION ####
            You are a teacher making a test for the class on certain topic given as a summary.

            #### TASK DESCRIPTION ####
            Make a test which consists of {request.num_questions} easy questions USING ONLY INFORMATION FROM THE SUMMARY.

            #### CRITICAL INSTRUCTIONS ####
            1. USE ONLY INFORMATION FROM THE SUMMARY - do not make questions that cannot be answered using the summary.
            2. ANSWERS MUST BE SHORT AND CONSIST OF ONLY 1-6 WORD - do not make long answers.
            3. EACH QUESTION SHOULD HAVE ONLY ONE CORRECT ANSWER - do not make questions with multiple correct answers.
            4. THE CORRECT ANSWER IS RANDOMLY COUNTED - do not make the correct answer the first one. It must stand in a randomly counted location.
            5. EACH QUESTION SHOULD HAVE 4 VARIANTS OF ANSWERS - do not make questions with less or more than 4 variants of answers.
            6. TOUCH EVERY TOPIC FROM THE SUMMARY - do not ignore any topic from the summary.
            7. IF THERE IS A FORMULA ADD IT - if there is a formula (for example E=mc^2) or equation ADD IT to the test as a question (for example FORMULA: E=mc^2 -> QUESTION: E=mx^2 What is X?)
            8. REPLY IN {request.language.upper()} LANGUAGE.

            #### FORMAT REQUIREMENTS ####
            - Use the exact XML tags as shown in the example below.
            - If no text is provided, still use the tags but state "no text provided"
            - Include ALL the topics from the summary in the test.

            Example format:
                <test>
                    <question>
                        <text>Question text</text>
                        <answer>
                            <text>Answer text</text>
                            <is_correct>true/false</is_correct>
                        </answer>
                        <answer>
                            <text>Answer text</text>
                            <is_correct>true/false</is_correct>
                        </answer>
                        <answer>
                            <text>Answer text</text>
                            <is_correct>true/false</is_correct>
                        </answer>
                        <answer>
                            <text>Answer text</text>
                            <is_correct>true/false</is_correct>
                        </answer>
                    </question>
                </test>
        
    """

    return await make_prompt(get_generate_payload(system_prompt=SYSTEM_PROMPT, prompt=request.text))

@router.post("/extract_text_from_pic", response_model=ImageTextResponse)
async def extract_text_from_pic(
    file: UploadFile = File(...),
    language: str = Form("auto")
):
    SYSTEM_PROMPT = f"""
    #### BASIC INFORMATION ####
    You are an assistant reading all the text from the pictures.

    #### TASK DESCRIPTION ####
    You get a picture in base64 format with text on it. Your task is to extract ALL the text from the picture and write the output.

    #### CRITICAL INSTRUCTIONS ####
    1. REPLY IN {language.upper()} LANGUAGE.
    2. READ ALL THE TEXT FROM THE PICTURE - read ALL the content in the picture. You MUST ADD ALL the text to the output.
    3. IF THERE IS NO TEXT IN THE PICTURE, STILL USE THE TAGS BUT STATE "no text provided"
    4. IF THERE IS A FORMULA ADD IT - if there is a formula or equation WRITE IT IN LATEX FORMAT.
    5. IF THERE IS A TABLE ADD IT - if there is a table ADD IT TO THE OUTPUT in the format below.

    #### FORMAT REQUIREMENTS ####
    - extract ALL THE TEXT from the picture.
    - use the exact XML tags as shown in the example below.
    - if there is no text in the picture, still use the tags but state "no text provided"
    - if there is no formula, DO NOT ADD THE FORMULA TAG.
    - if there is a formula, write it in the LATEX format.
    - if there is no table, DO NOT ADD THE TABLE TAG.
    - each new paragraph should be in a new <text> tag.


    Example format:
<picture_text>
    <text>
        Text of the picture
    </text>
    <formula>
        Formula in LATEX format (if there is one)
    </formula>
    <table>
        <row>
            <coloumn> coloumn name </coloumn>
            <coloumn> coloumn name </coloumn>
        </row>
        <row>
            <coloumn> coloumn name </coloumn>
            <coloumn> coloumn name </coloumn>
        </row>
    </table>
    <text>
        The continuation of the text
    </text>
</picture_text>    
    """
    contents = await file.read()
    encoded_image = base64.b64encode(contents).decode("utf-8")

    if len(contents) > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="The picture is too big. Max size: 20MB"
            )
    
    # Создаем payload для запроса
    payload = get_image_payload(system_prompt=SYSTEM_PROMPT, encoded_image=encoded_image)
    
    # Отправляем запрос и получаем ответ
    response = await make_prompt(payload)
    
    # Преобразуем ответ в формат ImageTextResponse
    return ImageTextResponse(
        text=response.response,
        language=language,
        raw_response=response.raw_response
    )



async def make_prompt(payload: dict):
    api_url = config['api_url']
    api_token = config['api_token']

    # Составляем URL с API-ключом
    full_url = f"{api_url}?key={api_token}"
    
    # Настройка заголовков
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Python version: {sys.version}")
    print(f"HTTPX version: {httpx.__version__}")
    
    try:
        # Более надежная конфигурация клиента с увеличенными таймаутами
        async with httpx.AsyncClient(
            timeout=60.0,
            verify=True,
            follow_redirects=True
        ) as client:
            print(f"Sending request to {api_url}")
            print(f"API Token (first 5 chars): {api_token[:5]}...")
            print(f"Headers: {headers}")
            print(f"Payload type: {type(payload).__name__}")
            
            response = await client.post(full_url, json=payload, headers=headers)
            
            # Логирование статуса и данных ответа для отладки
            print(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            # Извлечение сгенерированного текста из ответа AI
            generated_text = ""
            if "candidates" in result and len(result["candidates"]) > 0:
                for part in result["candidates"][0].get("content", {}).get("parts", []):
                    if "text" in part:
                        generated_text += part["text"]
            
            if not generated_text and "error" in result:
                error_message = result.get("error", {}).get("message", "Unknown error")
                error_code = result.get("error", {}).get("code", 500)
                
                # Handle specific error cases
                if error_code == 400 and "location" in error_message.lower():
                    raise HTTPException(
                        status_code=400,
                        detail="The Gemini API is not available in your current location. Please try using a VPN or check if the API is available in your region."
                    )
                elif error_code == 401:
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid API key. Please check your API key configuration."
                    )
                else:
                    raise HTTPException(
                        status_code=error_code,
                        detail=f"AI API error: {error_message}"
                    )
            
            return AIResponse(response=generated_text, raw_response=result)
            
    except httpx.HTTPStatusError as e:
        print(f"HTTP Status Error: {e}")
        print(f"Response status code: {e.response.status_code}")
        print(f"Response text: {e.response.text}")
        
        # Try to parse the error response
        try:
            error_data = e.response.json()
            error_message = error_data.get("error", {}).get("message", str(e))
            if "location" in error_message.lower():
                raise HTTPException(
                    status_code=400,
                    detail="The Gemini API is not available in your current location. Please try using a VPN or check if the API is available in your region."
                )
        except:
            pass
            
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"AI API error: {e.response.text}"
        )
    except httpx.ConnectError as e:
        print(f"Connection Error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Unable to connect to AI API: {str(e)}"
        )
    except httpx.ConnectTimeout as e:
        print(f"Connection Timeout: {e}")
        raise HTTPException(
            status_code=504,
            detail=f"Connection to AI API timed out: {str(e)}"
        )
    except httpx.ReadTimeout as e:
        print(f"Read Timeout: {e}")
        raise HTTPException(
            status_code=504,
            detail=f"Reading response from AI API timed out: {str(e)}"
        )
    except httpx.RequestError as e:
        print(f"Request Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to AI API: {str(e)}"
        )
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw response: {response.text}")
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON response from AI API: {str(e)}"
        )
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Unexpected error: {e}")
        print(traceback_str)
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with AI API: {str(e)}"
        )






def get_generate_payload(system_prompt: str, prompt: str):
    payload = {
        "contents": [
            {
                "role": "user", 
                "parts": [
                    {"text": system_prompt},
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": config['temperature'],
            "topP": config['top_p'],
            "maxOutputTokens": config['max_tokens']
        }
    }
    return payload


def get_image_payload(system_prompt, encoded_image):
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": system_prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": encoded_image
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,  # Низкая температура для более точного извлечения
            "topP": config['top_p'],
            "maxOutputTokens": config['max_tokens']
        }
    }
    return payload
