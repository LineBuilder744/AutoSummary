from fastapi import APIRouter, HTTPException, Depends, Header
import httpx
import json
import sys
import os
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from ai_prompts.config import config

# Создаем роутер для обработки запросов к /generate
router = APIRouter()


class AIRequest(BaseModel):
    text: str
    top_p: float = 0.95
    stream: bool = False
    additional_params: Optional[Dict[str, Any]] = None
    num_questions: int = 5


class AIResponse(BaseModel):
    response: str
    raw_response: Dict[str, Any]

@router.post("/generate_summary", response_model=AIResponse)
async def generate_summary(request: AIRequest):
    GENERATE_SUMMARY_PROMPT = f"""
            #### BASIC INFORMATION ####
            You are a student working on a making summary of the certain text.

            #### TASK DESCRIPTION ####
            Extract ALL the important information from the text. Your goal is to SUMMARIZE the text LEAVE ONLY IMPORTANT INFORMATION.

            #### CRITICAL INSTRUCTIONS ####
            1. DIVIDE THE TEXT INTO SMALL PIECES - each piece should have its own subtitle and text.
            2. SUMMARIZE THE TEXT - leave only important information. The output should be short and concise.
            3. DO NOT IGNORE FORMULAS - if there is a formula (for example E=mc^2) or equation ADD IT TO THE SUMMARY.
            4. DO NOT IGNORE DATES - if there is a date ADD IT TO THE SUMMARY.
            5. DO NOT IGNORE DEFINITIONS - if there is one ADD IT TO THE SUMMARY as a subtitle and description of it as a text.
            
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
            
            Here is the text that you must summarize: {request.text}
            """
    return await make_prompt(GENERATE_SUMMARY_PROMPT, request)


@router.post("/generate_test", response_model=AIResponse)
async def generate_test(request: AIRequest):

    GENERATE_TEST_PROMPT = f"""

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
            Here is the summary which you must use to make a test: {request.text}
    """
    return await make_prompt(GENERATE_TEST_PROMPT, request)


async def make_prompt(prompt: str, request: AIRequest):
    api_url = config['api_url']
    api_token = config['api_token']

    # Подготовка данных для запроса AI API
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": config['temperature'],
            "topP": request.top_p,
            "maxOutputTokens": config['max_tokens']
        }
    }
    
    # Добавляем дополнительные параметры, если они есть
    if request.additional_params:
        if "generationConfig" in payload:
            payload["generationConfig"].update(request.additional_params.get("generationConfig", {}))
        for key, value in request.additional_params.items():
            if key != "generationConfig":
                payload[key] = value
    
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
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = await client.post(full_url, json=payload, headers=headers)
            
            # Логирование статуса и данных ответа для отладки
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            print(f"Response content: {response.text[:200]}...")  # Печать первых 200 символов
            
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
                raise HTTPException(status_code=500, detail=f"AI API error: {error_message}")
            
            return AIResponse(response=generated_text, raw_response=result)
            
    except httpx.HTTPStatusError as e:
        print(f"HTTP Status Error: {e}")
        print(f"Response status code: {e.response.status_code}")
        print(f"Response text: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, 
                           detail=f"AI API error: {e.response.text}")
    except httpx.ConnectError as e:
        print(f"Connection Error: {e}")
        raise HTTPException(status_code=503, 
                           detail=f"Unable to connect to AI API: {str(e)}")
    except httpx.ConnectTimeout as e:
        print(f"Connection Timeout: {e}")
        raise HTTPException(status_code=504, 
                           detail=f"Connection to AI API timed out: {str(e)}")
    except httpx.ReadTimeout as e:
        print(f"Read Timeout: {e}")
        raise HTTPException(status_code=504, 
                           detail=f"Reading response from AI API timed out: {str(e)}")
    except httpx.RequestError as e:
        print(f"Request Error: {e}")
        raise HTTPException(status_code=500, 
                           detail=f"Error connecting to AI API: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        print(f"Raw response: {response.text}")
        raise HTTPException(status_code=500, 
                           detail=f"Invalid JSON response from AI API: {str(e)}")
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Unexpected error: {e}")
        print(traceback_str)
        raise HTTPException(status_code=500, 
                           detail=f"Error communicating with AI API: {str(e)}")

